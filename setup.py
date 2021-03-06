#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2016 Absolute Performance Inc <csteam@absolute-performance.com>.
# All rights reserved.
# This is proprietary software.
# No warranty, explicit or implicit, provided.

from setuptools import setup

from ssllabs import __author__, __description__, __email__, __license__, __modulename__, __version__, __website__

setup(
    name=__modulename__,
    version=__version__,
    description=__description__,
    author=__author__,
    author_email=__email__,
    url=__website__,
    license=__license__,
    entry_points={
        'console_scripts': [
            'ssllabs-gradecheck = ssllabs.__main__:gradecheck',
            ]
        },
    packages=[
        'ssllabs',
        ],
    install_requires=[
        'six',
        'requests',
        'enum34',
        'tqdm',
        ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security'
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
)
