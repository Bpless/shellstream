#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import datetime
import subprocess
from optparse import OptionParser
from multiprocessing import Process

from utils import *
from worker import Worker
from client import Client


class StreamingShell(object):
    shell_output_dir = "~/"
    worker_pid_fname = "worker_pid"
    parent_pid_fname = "parent_pid"

    def __init__(self, username="bob", password="test"):
        self.username = username
        self.password = password
        self.client = self._authenticate(username, password)

    def __enter__(self):
        return self._log_start()._write_pid()._init_script_file()

    def __exit__(self, type, value, traceback):
        try:
            f = open(self.parent_pid_fname, "r")
            if not os.getpid() == int(f.read()):
                return
        except IOError:
            pass

        os.remove(self.parent_pid_fname)
        os.remove(self.shell_output_path)

        try:
            with open(self.worker_pid_fname, "r") as f:
                os.kill(int(f.read()), 9)
                os.remove(self.worker_pid_fname)
        except OSError, e:
            logger.warning(e)
        except IOError, e:
            logger.warning(e)
        except ValueError:
            logger("Worker pid file does not contain valid pid")

    def start(self):
        if os.fork() == 0:
            # In child process
            with open(self.worker_pid_fname, "w") as f:
                f.write("{}".format(os.getpid()))
            self._start_worker()
        else:
            self._start_recording()

    def _authenticate(self, username, password):
        client = Client(username, password)

        try:
            client.authenticate()
        except client.AuthenticationError:
            print_red("Failed to authenticate the username/password combination")
            sys.exit(1)
        else:
            return client

    def _write_pid(self):
        pid = os.getpid()
        with open(self.parent_pid_fname, "w") as f:
            f.write("{}".format(pid))
        return self

    def _init_script_file(self):
        self.shell_pid = os.getppid()
        timestamp = datetime.datetime.now().isoformat()
        self.shell_output_path = f_name = "streaming_shell.{}.{}.txt".format(self.shell_pid, timestamp)
        with open(f_name, "w"):
            pass
        return self

    def _start_worker(self):
        Worker(self.client, self.shell_output_path).labor()

    def _start_recording(self):
        current_ps1 = os.environ.get("PS1")
        bash_prompt_cmd = 'export PS1="[SHDEBUG]{}"'.format(current_ps1)
        cmd = "{};script -q -t 0 {}".format(bash_prompt_cmd, self.shell_output_path)
        # Blocks
        res = subprocess.call(cmd, shell=True)
        # User exited mainloop, time to kill worker process


        # return self._set_bash_prompt()._exec_script()

    # def _exec_script(self):
    #     cmd = "script -q -t 0 {} \n".format(self.shell_output_path)
    #     self.recording_process.stdin.write(cmd)
    #     self._reset_stdin()
    #     self.recording_process.wait()
    #     return self

    # def _reset_stdin(self):
    #     self.recording_process.stdin.flush()
    #     self.recording_process.stdin.close()
    #     self.recording_process.stdin = sys.stdin
    #     return self

    # def _set_bash_prompt(self):
    #     current_ps1 = os.environ.get("PS1")
    #     bash_prompt_cmd = 'export PS1="[SHDEBUG]{}" \n'.format(current_ps1)
    #     self.recording_process.stdin.write(bash_prompt_cmd)
    #     return self

    def _log_start(self):
        print_green(">>>> ......................")
        print_green(">>>> ......................")
        print
        print_green(">>>> Beginning StreamingShell mode")
        print_green(">>>> All of your commands within THIS SHELL will be piped to pusher.com")
        print_green(">>>> To exit this mode, press the following keys")
        print_blue("\tctrl + d", ["bold", "underline"])
        print

        print_green(">>>> ......................")
        print_green(">>>> ......................")
        return self


if __name__ == "__main__":

    usage = "usage: %prog --username=[YOUR USERNAME] --password=[PASSWORD]"
    parser = OptionParser(usage)
    parser.add_option("-u", "--username", dest="username",
                      action="store", type="string",
                      help="account username[required]")
    parser.add_option("-p", "--password", dest="password",
                      action="store", type="string",
                      help="account password[required]")

    options, args = parser.parse_args()

    with StreamingShell(options.username, options.password) as shell:
        shell.start()
