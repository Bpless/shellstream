#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <shellstream - pipe your terminal IO to the cloud in python>
# Copyright (C) <2013>  Benjamin Plesser <benjamin.plesser@gmail.com>
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

import re
import os
from setuptools import setup, find_packages


def parse_requirements():
    """Rudimentary parser for the `requirements.txt` file

    We just want to separate regular packages from links to pass them to the
    `install_requires` and `dependency_links` params of the `setup()`
    function properly.
    """
    try:
        requirements = \
            map(str.strip, local_file('requirements.txt').splitlines())
    except IOError:
        raise RuntimeError("Couldn't find the `requirements.txt' file :(")

    links = []
    pkgs = []
    for req in requirements:
        if not req:
            continue
        if 'http:' in req or 'https:' in req:
            links.append(req)
            name, version = re.findall("\#egg=([^\-]+)-(.+$$)", req)[0]
            pkgs.append('{0}=={1}'.format(name, version))
        else:
            pkgs.append(req)

    return pkgs, links


def find_scripts():
    """
    Simple Script to find any files to place in the bin/ directory after
    installation.
    """
    scripts_directory = "shellstream/scripts"
    scripts = []
    try:
        files = os.listdir(os.path.join(os.path.dirname(__file__), scripts_directory))
        for f in files:
            scripts.append("{scripts_dir}/{file}".format(scripts_dir=scripts_directory, file=f))
    except:
        pass
    return scripts


local_file = lambda f: open(os.path.join(os.path.dirname(__file__), f)).read()
install_requires, dependency_links = parse_requirements()


if __name__ == '__main__':

    setup(
        name="shellstream",
        version='0.0.2.0',
        description="Python program that pipes your terminal to the cloud",
        long_description=local_file('README.md'),
        author='Benjamin Plesser',
        author_email='benjamin.plesser@gmail.com',
        url='https://github.com/Bpless/shellstream',
        packages=find_packages(exclude=['*tests*']),
        install_requires=install_requires,
        dependency_links=dependency_links,
        entry_points={
                'console_scripts': [
                    'startstream = shellstream.main:run',
                ]
        },
        classifiers=[
            'Programming Language :: Python',
        ],
        zip_safe=False,
    )
