#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='dumbrain',
    version='0.1',
    description='Dumbrain AI Monorepo',
    author='Mike Lyons',
    author_email='mdl0394@gmail.com',
    packages=find_packages( exclude=[ 'tmp' ] )
)
