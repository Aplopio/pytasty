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
    version='0.1dev',
    packages=['pytasty', ],
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=[
        # -*- Extra requirements: -*-
        'requests == 2.2.1',
    ],
)
