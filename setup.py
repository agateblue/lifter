#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lifter

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
    'six',
]

test_requirements = [
    'six',
    'mock', # TODO: put package test requirements here
    'requests_mock',
]

setup(
    name='lifter',
    version=lifter.__version__,
    description="A lightweight query engine for Python iterables, inspired by Django ORM",
    long_description=readme + '\n\n' + history,
    author="Eliot Berriot",
    author_email='contact@eliotberriot.com',
    url='https://github.com/eliotberriot/lifter',
    packages=[
        'lifter',
    ],
    package_dir={'lifter':
                 'lifter'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='lifter',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
