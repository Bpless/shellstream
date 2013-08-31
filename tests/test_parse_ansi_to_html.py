#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from shellstream.worker import ShellReader

sample_stream = os.path.abspath(os.path.join(os.path.dirname(__file__), "sample_stream.txt"))
html_unescaped = """<pre>[SHDEBUG](shdebugger)<span class="ansi1 ansi32">benjaminplesser@laptop:<span class="ansi1 ansi34">~/.virtualenvs/shdebugger/streamer $</span></span> </pre> <pre>ls </pre> <pre>-</pre> <pre></pre> <pre></pre> <pre>README.md        __init__.py      __init__.pyc     requirements.txt <span class="ansi34">shellstream<span class="ansi39 ansi49"></span></span>      <span class="ansi34">tests<span class="ansi39 ansi49"></span></span></pre>"""
html_escaped = """[pr][SHDEBUG](shdebugger)[sp] class="ansi1 ansi32"[--]benjaminplesser@laptop:[sp] class="ansi1 ansi34"[--]~/.virtualenvs/shdebugger/streamer $[/sp][/sp] [/pr] [pr]ls [/pr] [pr]-[/pr]   [pr]README.md        __init__.py      __init__.pyc     requirements.txt [sp] class="ansi34"[--]shellstream[sp] class="ansi39 ansi49"[--][/sp][/sp]      [sp] class="ansi34"[--]tests[sp] class="ansi39 ansi49"[--][/sp][/sp][/pr]"""


def unescaped_html_content(html):
    import re

    def translate(object):
        translations = {
                "[pre]": "<pre>",
                "[/pre]": "</pre>",
                "[sp]": "<span",
                "[/sp]": "</span>",
                "[div]": "<div",
                "[/div]": "</div>",
                "[--]": ">"
            }
        return translations[object.group()]

    regex_map = [
                    "\[pre\]",
                    "\[/pre\]",
                    "\[sp\]",
                    "\[/sp\]",
                    "\[div\]",
                    "\[/div\]",
                    "\[--\]"
                ]

    matcher = "|".join([key for key in regex_map])
    res = re.sub(r"{0}".format(matcher), translate, html)
    import ipdb; ipdb.set_trace()

def test_reader():
    class MockQueue(object):
        def __init__(self):
            self.data = []

        def put(self, output):
            self.data.append(output)

    reader = ShellReader()
    reader.f_name = sample_stream
    reader.queue = MockQueue()
    reader.do_work()
    unescaped_html_content(reader.queue.data[2])
    import ipdb; ipdb.set_trace()


def test_escape_html():
    reader = ShellReader()
    value = reader.escape_html(html_unescaped)
    assert value == html_escaped, "Escaping html failed"

