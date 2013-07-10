#!/usr/bin/env python
from shellstream.shell import StreamingShell


def run():
    with StreamingShell() as shell:
        shell.stream()
