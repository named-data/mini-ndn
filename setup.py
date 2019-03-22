#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "MiniNDN-WiFi",
    version = '0.4.1',
    packages = find_packages(),
    scripts = ['bin/minindn', 'bin/minindnedit'],
)
