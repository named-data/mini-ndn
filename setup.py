#!/usr/bin/env python

from setuptools import setup, find_packages
from minindn import __version__

setup(
    name = "Mini-NDN",
    version = __version__,
    description='Mininet based NDN emulator',
    packages = find_packages(),
)

print(find_packages())
