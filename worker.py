#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiprocessing import Process, Queue
import time
import sys
import os
from ansi2html import Ansi2HTMLConverter
from Queue import Queue
import threading

queue = Queue()


class DataWriter(threading.Thread):

    #----------------------------------------------------------------------
    def __init__(self, queue, client):
        super(DataWriter, self).__init__()
        self.daemon = True
        self.queue = queue
        self.client = client
        self.failures = 0
        self.max_failures = 3
        print threading.current_thread().ident
        print "In data writer pid {}".format(os.getpid())

    def run(self):
        with open("writer.html", "w") as f:
            while True:
                html = self.queue.get()
                self.write(f, html)
                # Probably unnecessary
                self.queue.task_done()

    def write(self, f, data):
        f.write(data)
        return f.flush()

        ########
        try:
            self.client.post(data)
        except self.client.WriteFailed:
            self.failures += 1
            if self.failures > self.max_failures:
                pass
                # Stop all processes


class DataReader(threading.Thread):

    def __init__(self, queue, f_name, bufsize=5120):
        super(DataReader, self).__init__()
        self.daemon = True
        self.f_name = f_name
        self.queue = queue
        self.bufsize = bufsize
        print threading.current_thread().ident
        print "In data reader pid {}".format(os.getpid())

    def run(self):
        lines = []
        for line in self.tail():
            if line:
                html = self.parse_line(line)
                lines.append(html)
                if len(lines) > 10:
                    buffered_html = " ".join(lines)
                    self.queue.put(buffered_html)
                    lines = []

    def tail(self):
        with open(self.f_name, "r") as _input:
            while True:
                time.sleep(1)
                yield _input.readline()

    def parse_line(self, line):
        conv = Ansi2HTMLConverter()
        # differentiate here between user input and output
        html = conv.convert(ansi=line, full=False).strip("\r\n").replace("[?1034h", "")
        return "<pre>{}</pre>".format(html)



# class ScriptOutputReader(object):
#     def __init__(self, file_name, bufsize=5120):
#         self.watched_fname = file_name
#         self.bufsize = bufsize
#         self.queue = queue

#     def run(self):
#         lines = []
#         for line in self.tail():
#             if line:
#                 html = self.parse_line(line).strip("\r\n")
#                 lines.append(html)
#                 if len(lines) > 10:
#                     queue.put(" ".join(lines))


#     def tail(self):
#         with open(self.watched_fname, "r") as _input:
#             while True:
#                 time.sleep(1)
#                 yield _input.readline()

#     def parse_line(self, line):
#         conv = Ansi2HTMLConverter()
#         html = conv.convert(ansi=line, full=False).strip("\r\n")
#         return "<pre>{}</pre>".format(html)

        # def _wrap(line):
        #     _line_buffer = []
        #     _ansi_escape_buffer = []
        #     trailing_char = None
        #     for char in line.strip():
        #         if not _ansi_escape_buffer:
        #             if char == "\\":
        #                 _ansi_escape_buffer.append(char)
        #             else:
        #                 _line_buffer.append(char)
        #         else:
        #             _ansi_escape_buffer.append(char)
        #             ansi_partial = validate_ansi(_ansi_escape_buffer)
        #             if ansi_partial.is_valid():
        #                 if ansi_partial.complete:
        #                     _line_buffer.append(str(ansi_partial))
        #                 else:
        #                     continue
        #             else:
        #                 # We are not actually insdie of an escape
        #                 _line_buffer.extend(_ansi_escape_buffer)
        #                 _ansi_escape_buffer = []

        #             if line:
        #                 yield_output.write(line)
        #                 _output.flush()


class Worker(object):

    def __init__(self, client, f_name):
        self.client = client
        self.f_name = f_name

    def labor(self):
        reader = DataReader(queue, self.f_name)
        writer = DataWriter(queue, self.client)

        reader.daemon = True
        writer.daemon = True

        reader.start()
        writer.start()
        reader.join()
        print 'finished this shit'
