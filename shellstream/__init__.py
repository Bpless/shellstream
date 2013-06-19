#!/usr/bin/env python
# -*- coding: utf-8 -*-
from shellstream.shell import StreamingShell


if __name__ == "__main__":
    with StreamingShell() as shell:
        shell.stream()
