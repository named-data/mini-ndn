#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "Mini-NDN",
    version = '0.2.0',
    packages = find_packages(),
    scripts = ['bin/minindn', 'bin/minindnedit'],
)
