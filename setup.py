#!/usr/bin/env python

from __future__ import with_statement

from distutils.core import setup

with open('README.md') as ld_file:
    long_description = ld_file.read()

setup(
    name = "django-utils",
    version = "0.1",
    description = "A collection of utility models for Django",
    long_description = long_description,
    author = "Jesse the Game",
    author_email = "jesse@jessethegame.net",
    url = "http://github.com/jessethegame/django-utils",
    license = "MIT License",
    py_modules = ['utils'],
)

