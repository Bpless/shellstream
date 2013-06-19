#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import atexit
import glob
import os
import datetime
import subprocess
import logging
logger = logging.getLogger(__name__)
from optparse import OptionParser

from .backends.http import TransportError
from .utils.io import *
from .worker import Worker
from .config import Config, HOST, BASH_PROMPT

# # Normal exit when killed
# signal(SIGTERM, lambda signum, stack_frame: exit(1))


class StreamingShell(object):

    def __init__(self):
        Config(self)
        self.parent_pid = os.getpid()
        self.timestamp = datetime.datetime.now().isoformat()
        atexit.register(self.on_abrupt_exit)

    def __enter__(self):
        self._display_intro()
        self._validate_output_dir()
        self._validate_user_input()
        self.authenticate()
        self._init_local_stream_file()
        self.create_remote_stream()
        self._write_pid(self._parent_pid_path, self.parent_pid)
        return self

    def __exit__(self, type, value, traceback):
        if self.in_main_loop():
            self._cleanup_processes()

    def on_abrupt_exit(self):
        self._cleanup_processes()

    def in_main_loop(self):
        try:
            with open(self._parent_pid_path, "r") as parent_pid_file:
                parent_pid = parent_pid_file.read()
                if os.getpid() == int(parent_pid):
                    # We are in child, no need to cleanup twice
                    return True
        except IOError:
            return False

    def _cleanup_processes(self):
        try:
            os.remove(self._parent_pid_path)
            os.remove(self._shell_output_path)
            self._clean_child_process()
        except OSError:
            pass

    def _clean_child_process(self):
        try:
            child_pid_path = glob.glob("{}child_pid.{}.*".format(self.output_dir, self.parent_pid))[0]
            with open(child_pid_path, "r") as child_pid_file:
                child_pid = child_pid_file.read()

            os.remove(child_pid_path)
            os.kill(int(child_pid), 9)
        except (OSError, IOError, IndexError, ValueError), e:
            logger.warning(e)

    @classmethod
    def create_user(cls):
        shell = cls()
        Config(shell)
        shell._validate_credentials()
        transport = shell.TransportKls(username=shell.username, password=shell.password)
        try:
            transport.create_user()
        except TransportError, e:
            print_red("\nSignup Failure:\n{}\n".format(e))
            sys.exit(1)
        else:
            print_green("\nAlmost there. To Activate {}".format(shell.username))
            print_green("Check your inbox for an activation email")
            print_blue("Paste the confirmation link below to the activate your account")
            url = None
            while True:
                url = raw_input(">>>> ENTER THE URL:  ")
                try:
                    transport.activate_user(url)
                except TransportError:
                    print_red("\nActivation Error: Invalid URL")
                else:
                    print_green("\nSuccess, your account has been activated!!")
                    break

    def stream(self):
        if os.fork() == 0:
            # In child process
            self._write_pid(self._child_pid_path, os.getpid())
            self._start_worker()
        else:
            self._start_recording()

    def authenticate(self):
        try:
            self.transport.authenticate()
        except TransportError, e:
            print_red("\nFailed during login\n{}\n".format(e))
            sys.exit(1)

    def _init_local_stream_file(self):
        subprocess.call("touch {}".format(self._shell_output_path), shell=True)

    def create_remote_stream(self):
        try:
            stream_id, stream_slug = self.transport.create_stream()
            stream_url = "{}stream/{}/{}/".format(HOST, stream_id, stream_slug)
            prompt(print_green, "\nAll of your commands within THIS SHELL will be piped to {}".format(stream_url))
            subprocess.call("open {}".format(stream_url), shell=True)
        except TransportError, e:
            print_red("\nFailed to create stream:\n{}\n".format(e))
            sys.exit(1)

    def _write_pid(self, path, pid):
        with open(path, "w") as f:
            f.write("{}".format(pid))
        return self

    @property
    def _child_pid_path(self):
        return "{}child_pid.{}.{}.{}.txt".format(self.output_dir, self.parent_pid, os.getpid(), self.timestamp)

    @property
    def _parent_pid_path(self):
        return "{}parent_pid.{}.{}.txt".format(self.output_dir, self.parent_pid, self.timestamp)

    @property
    def _shell_output_path(self):
        return "{}streaming_shell.{}.{}.txt".format(self.output_dir, self.parent_pid, self.timestamp)

    def _start_worker(self):
        Worker.labor(self.transport, self._shell_output_path, self.parent_pid)

    def _start_recording(self):
        current_ps1 = os.environ.get("PS1")
        bash_prompt_cmd = 'export PS1="{}{}"'.format(BASH_PROMPT, current_ps1)
        cmd = "{};script -q -t 0 {}".format(bash_prompt_cmd, self._shell_output_path)
        # This call blocks
        res = subprocess.call(cmd, shell=True)

    def _display_intro(self):
        print
        prompt(print_green, "Beginning StreamingShell mode [writing to {}]".format(self.output_dir))
        prompt(print_green, "To exit this mode, press the following keys")
        print_blue("\tctrl + d", ["bold", "underline"])
        print

        return self

    def _validate_user_input(self):
        self._validate_credentials()
        self._validate_title()

    def _validate_credentials(self):
        if not (self.username and self.password):
            print
            prompt(print_magenta, "Before you stream, you'll need to enter a username and password")
            prompt(print_magenta, "If you do not have an account, you can create one by executing the command")
            print_blue("\tstreamshell create --username=[username] --password=[password]", ["bold", "underline"])
            print
            prompt(print_magenta, "Already have an account? Pass your credentials as command line arguments to streamshell")
            print_blue("\tstreamshell --username=[username] --password=[password]", ["bold", "underline"])
            print
            prompt(print_magenta, "Or you can set the SHELL_STREAM_USERNAME, SHELL_STREAM_PASSWORD environment variables")
            print_blue("\texport SHELL_STREAM_USERNAME=[username] SHELL_STREAM_PASSWORD=[password]", ["bold", "underline"])
            prompt(print_magenta, "Add the above export command to your ~./bash_profile for extra convienence")

            if not self.username:
                self.username = wait_for_response(5, ">>>> ENTER USERNAME: ")
            if not self.password:
                self.password = wait_for_response(5, ">>>> ENTER PASSWORD: ")
            import ipdb; ipdb.set_trace()

    def _validate_output_dir(self):
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

    def _validate_title(self):
        if not self.title:
            self.title = wait_for_response(5, ">>>> ENTER SESSION TITLE [>5 chars]: ")
