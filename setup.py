#!/usr/bin/env python
#
# Copyright 2016, Cisco Systems
# All Rights Reserved.
#

import os
import setuptools

from pip.download import PipSession
from pip.req import parse_requirements

def reqs(path):
    return [str(r.req) for r in parse_requirements(path, session=PipSession())
            if r.req]

INSTALL_REQUIRES = reqs("requirements.txt")
TESTS_REQUIRE = reqs("test-requirements.txt")

setuptools.setup(
    name='genetisnake',
    version='0.1.0',
    url='https://github.com/noelbk/genetisnake-python',
    description='Battlesnake Python client',
    author='Noel Burton-Krahn <noel@burton-krahn.com>',
    author_email='noel@burton-krahn.com',
    packages=setuptools.find_packages(exclude=['tests']),
    package_dir={'genetisnake': 'genetisnake'},
    include_package_data=True,
    setup_requires=['tox-setuptools'],
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require=dict(
        test=TESTS_REQUIRE,
        tests=TESTS_REQUIRE,
        ),
    entry_points={
        'console_scripts': [
            'training = genetisnake.training:evolve',
            ],
        },
    
)
