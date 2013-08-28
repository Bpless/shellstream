#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import atexit
import glob
import datetime
import subprocess
import platform
import json
import webbrowser

import logging
logger = logging.getLogger(__name__)

from shellstream.transport import TransportError
from shellstream.utils.io import *
from shellstream.worker import Worker
from shellstream import BASH_PROMPT
from shellstream.authentication import TokenGenerator
from shellstream.config import Config


class StreamingShell(object):

    def __init__(self):
        Config(self)
        self.parent_pid = os.getpid()
        # TODO: either change this to a timestap or refer to it as datetime
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

    def stream(self):
        if os.fork() == 0:
            # In child process
            self._write_pid(self._child_pid_path, os.getpid())
            self._start_worker()
        else:
            self._start_recording()

    def authenticate(self):
        tokenizer = TokenGenerator(self.token)
        encrypted_token = tokenizer.encode_token()

        try:
            self.transport.fetch("api/login/", {"encrypted_token": encrypted_token}, response_callback=self.transport.set_session_id)
        except TransportError, e:
            print_red("\nFailed during login\n{0}\n".format(e))
            sys.exit(1)

    def create_remote_stream(self):
        try:
            self.create_stream()
        except TransportError, e:
            print_red("\nFailed to create stream:\n{0}\n".format(e))
            sys.exit(1)
        else:
            stream_url = "http://www.enginehere.com/stream/{0}/{1}/".format(self.stream_id, self.stream_slug)
            prompt(print_green, "\nAll of your commands within THIS SHELL will be piped to {0}".format(stream_url))
            # Commenting this out for now, since I'm using a terminal without any x windows.
            # webbrowser.open_new_tab(stream_url)

    def create_stream(self):
        data = self.get_system_info()
        data["title"] = self.title

        content = self.transport.fetch("api/stream/create/", data)
        self.stream_id = content.get("stream_id")
        self.stream_slug = content.get("stream_slug")

    def get_system_info(self):
        data = {}

        system, node, release, version, machine, processor = platform.uname()
        if system and "darwin" in system.lower():
            data["os"] = "Mac OS X"
            data["os_version"] = platform.mac_ver()[0]
        else:
            data["os"] = system

        data["machine"] = machine
        data["path"] = sys.path
        data["cwd"] = os.getcwd()

        data["python_version"] = ".".join([str(component) for component in sys.version_info[:3]])
        data["python_executable"] = sys.executable

        try:
            data["username"] = subprocess.Popen("id -n -u", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
            user_id = subprocess.Popen("id -u", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
            if user_id:
                data["user_id"] = int(user_id)
        except subprocess.CalledProcessError:
            pass

        try:
            data["pip_installed_packages"] = subprocess.Popen("pip freeze", shell=True, stdout=subprocess.PIPE.stdout.read()
        except subprocess.CalledProcessError:
            data["pip_installed_packages"] = "Unknown: pip not installed"

        return {"system_info": json.dumps(data)}

    def _write_pid(self, path, pid):
        with open(path, "w") as f:
            f.write("{0}".format(pid))
        return self

    @property
    def _child_pid_path(self):
        return "{0}child_pid.{1}.{2}.{3}.txt".format(self.output_dir, self.parent_pid, os.getpid(), self.timestamp)

    @property
    def _parent_pid_path(self):
        return "{0}parent_pid.{1}.{2}.txt".format(self.output_dir, self.parent_pid, self.timestamp)

    @property
    def _shell_output_path(self):
        return "{0}streaming_shell.{1}.{2}.txt".format(self.output_dir, self.parent_pid, self.timestamp)

    def _start_worker(self):
        Worker.labor(self.transport, self._shell_output_path, self.parent_pid, self.stream_id)

    def _start_recording(self):
        current_ps1 = os.environ.get("PS1", "\\w $\\[\\033[00m\\]")
        bash_prompt_cmd = 'export PS1="{0}{1}"'.format(BASH_PROMPT, current_ps1)
        # Be quite and flush output after each write.
        cmd = "{0};script -q -f {1}".format(bash_prompt_cmd, self._shell_output_path)
        # This call blocks
        subprocess.call(cmd, shell=True)

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
            child_pid_path = glob.glob("{0}child_pid.{1}.*".format(self.output_dir, self.parent_pid))[0]
            with open(child_pid_path, "r") as child_pid_file:
                child_pid = child_pid_file.read()

            os.remove(child_pid_path)
            os.kill(int(child_pid), 9)
        except (OSError, IOError, IndexError, ValueError), e:
            logger.warning(e)

    def _init_local_stream_file(self):
        subprocess.call("touch {0}".format(self._shell_output_path), shell=True)

    def _display_intro(self):
        print
        prompt(print_green, "Beginning StreamingShell mode [writing to {0}]".format(self.output_dir))
        prompt(print_green, "To exit this mode, press the following keys")
        print_blue("\tctrl + d", ["bold", "underline"])
        print

        return self

    def _validate_user_input(self):
        self._validate_credentials()
        self._validate_title()

    def _validate_credentials(self):
        if not (self.token):
            print
            prompt(print_magenta, "In order to create tickets, you'll need to provide an API token")
            prompt(print_magenta, "If you do not already have an account, please sign up!")
            print_blue('Otherwise visit: "http://www.enginehere.com/how/it/works/cli/" to grab your token', ["bold", "underline"])

            print
            prompt(print_magenta, "You can pass your token as a command line argument")
            print_blue("\tstreamshell --api_token=[your token]", ["bold", "underline"])
            print
            prompt(print_magenta, "Or you can set the SHELL_STREAM_TOKEN environment variable with the command")
            print_blue("\texport SHELL_STREAM_TOKEN=[your token]", ["bold", "underline"])
            prompt(print_magenta, "Add the above export command to your ~/.bash_profile file for extra convienence")

            if not self.token:
                self.token = wait_for_response(5, ">>>> ENTER TOKEN: ")

    def _validate_output_dir(self):
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

    def _validate_title(self):
        if not self.title:
            self.title = wait_for_response(5, ">>>> ENTER ISSUE TITLE [>5 chars]: ")
