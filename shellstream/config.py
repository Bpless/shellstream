#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tempfile
from optparse import OptionParser

from shellstream.transport import HttpTransport


class Config(object):

    def __init__(self, streamer):
        usage = "usage: %prog --token=[your token]"
        parser = OptionParser(usage)
        parser.add_option("-o", "--output_dir", dest="output_dir",
                          action="store", type="string",
                          help="directory where the streaming files are stored"),
        parser.add_option("-a", "--api_token", dest="token",
                          action="store", type="string",
                          help="your api token"),
        parser.add_option("-t", "--title", dest="title",
                          action="store", type="string",
                          help="the title of the ticket")
        parser.add_option("-v", "--verbose", dest="verbose",
                          action="store", type="string",
                          help="Set logging level to verbose")

        options, args = parser.parse_args()

        streamer.token = options.token or os.getenv("SHELL_STREAM_TOKEN")
        streamer.title = options.title
        streamer.transport = HttpTransport()
        streamer.output_dir = options.output_dir or "{}/streamshell/".format(tempfile.gettempdir())
