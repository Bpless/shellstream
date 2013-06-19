#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tempfile
import importlib
from optparse import OptionParser

HOST = "http://127.0.0.1:8000/"
BASH_PROMPT = "[SHSTREAM]"


class Config(object):

    def __init__(self, streamer):
        usage = "usage: %prog --username=[YOUR USERNAME] --password=[PASSWORD]"
        parser = OptionParser(usage)
        parser.add_option("-b", "--backend", dest="backend",
                      action="store", type="string",
                      help="Backend [http or file]")
        parser.add_option("-o", "--output_dir", dest="output_dir",
                          action="store", type="string",
                          help="account password[required]"),
        parser.add_option("-p", "--password", dest="password",
                          action="store", type="string",
                          help="account password"),
        parser.add_option("-t", "--title", dest="title",
                      action="store", type="string",
                      help="account password[required]")
        parser.add_option("-u", "--username", dest="username",
                          action="store", type="string",
                          help="account username")
        parser.add_option("-v", "--verbose", dest="verbose",
                          action="store", type="string",
                          help="Set logging level to verbose")

        options, args = parser.parse_args()

        streamer.username = options.username or os.getenv("SHELL_STREAM_USERNAME")
        streamer.password = options.password or os.getenv("SHELL_STREAM_PASSWORD")
        streamer.title = options.title
        streamer.transport = self.init_transport(streamer, options)
        # TODO: Use correct os.path.sep here
        streamer.output_dir = options.output_dir or "{}/streamshell/".format(tempfile.gettempdir())

    def init_transport(self, streamer, options):
        if options.backend == "file":
            backend_path = "shellstream.backends.file"
        else:
            backend_path = "shellstream.backends.http"

        TransportKls = getattr(importlib.import_module(backend_path), 'transport')
        return TransportKls(username=streamer.username, password=streamer.password, title=streamer.title)
