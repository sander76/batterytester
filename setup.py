#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

from batterytester.__version__ import __version__ as VERSION

# Package meta-data.
EMAIL = None
AUTHOR = "Sander Teunissen"
REQUIRES_PYTHON = ">=3.5.0"


setup(
    name="batterytester",
    version=VERSION,
    packages=find_packages(exclude="test"),
    url="",
    license="",
    author=AUTHOR,
    description="Batterytester framework",
    install_requires=[
        "pyserial==3.4",
        "aiopvapi==1.6.14",
        "aiohttp==3.7.4",
        "python-slugify==1.2.5",
        "aiotg==0.9.9",
        "async_timeout==3.0.1",
    ],
)
