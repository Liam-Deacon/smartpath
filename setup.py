#!/usr/bin/env python
# -*- coding: utf8 -*-
import os

from setuptools import setup, find_packages

root = os.path.abspath(os.path.dirname(__file__)) + '/'

setup(
    name='smartpath',
    version=open(root + 'VERSION', 'r').read().strip('\n'),
    description='Intelligently handle URI paths similar to pathlib',
    long_description=open(root + 'README.md', 'r').read(),
    license='MIT License',
    author='Liam Deacon',
    author_email='liam.m.deacon@gmail.com',
    url='https://github.com/LightSlayer/smartpath',
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(),
    install_requires=open(root + 'requirements.txt', 'r').readlines(),
    extras_require={
        ":python_version<'3.0'": ['futures'],
    },
)
