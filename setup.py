#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine
# python setup.py upload

import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = "batterytester"
DESCRIPTION = "Batterytester framework"
URL = "https://github.com/sander76/aio-powerview-api"
EMAIL = None
AUTHOR = "Sander Teunissen"
REQUIRES_PYTHON = ">=3.5.0"
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = [
    "pyserial",
    "aiopvapi",
    "aiohttp==3.3.2",
    "python-slugify",
    "aiotg",
    "telepot",
    "async_timeout",
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember
# to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system(
            "{0} setup.py sdist bdist_wheel --universal".format(sys.executable)
        )

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        sys.exit()


setup(
    name=NAME,
    version=about["__version__"],
    packages=find_packages(exclude="test"),
    url="",
    license="",
    author=AUTHOR,
    description="",
    install_requires=REQUIRED,
    # $ setup.py publish support.
    cmdclass={"upload": UploadCommand},
)
