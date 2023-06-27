#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
setup(
    name='pytasty',
    version='0.4.0',
    packages=['pytasty', ],
    license='MIT',
    long_description=open('README.rst').read(),
    install_requires=[
        'requests >= 2.26.0',
    ],
)
