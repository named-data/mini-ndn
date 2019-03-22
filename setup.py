#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "MiniNDN-WiFi",
    version = '0.1.0',
    packages = find_packages(),
    scripts = ['bin/minindn', 'bin/minindnedit'],
)
