#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from functools import partial
from termcolor import colored, cprint


def wait_for_response(min_chars, prompt):
    output = ""
    while len(output) < min_chars:
        print
        output = raw_input(prompt)
    return output


def prompt(func, text):
    func(">>>> {0}".format(text))


def color_print(color, msg, attrs=None):
    text = colored(msg, color, attrs=attrs)
    cprint(text)


def init_printers():
    mod = sys.modules[__name__]
    mod.__dict__.setdefault('__all__', ["wait_for_response", "prompt"])

    for color in ["red", "green", "yellow", "magenta", "blue", "grey", "cyan"]:
        f = partial(color_print, color)
        fname = "print_{0}".format(color)
        if color not in mod.__dict__:  # Prevent overrides if run from an IDE.
            mod.__dict__[fname] = f
            mod.__dict__["__all__"].append(fname)


init_printers()
