#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
if "--setuptools" in sys.argv:
    sys.argv.remove("--setuptools")
    from setuptools import setup
else:
    from distutils.core import setup
from imp import load_source

import pybitly

README = open('README').read().strip()
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet',
]

setup(
    name=pybitly.NAME,
    version=pybitly.VERSION,
    description='A python binding for the Bit.ly API',
    long_description=README,
    author=pybitly.AUTHOR,
    author_email='mattoufootu@gmail.com',
    url='http://github.com/mattoufoutu/pybitly',
    license='GPL',
    classifiers=CLASSIFIERS,
    packages=['pybitly'],
)
