#!/usr/bin/env python

import os
import re
import sys
# from codecs import open

from setuptools import (setup, find_packages)
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload -r pypi')
    sys.exit()

requires = ['pyyaml']
test_requirements = ['pytest>=2.9.2', 'pytest-cov>=2.3.0']

with open('lib/creds/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

# with open('README.rst', 'r', 'utf-8') as f:
#     readme = f.read()
# with open('HISTORY.rst', 'r', 'utf-8') as f:
#     history = f.read()

setup(
    name='creds',
    version=version,
    description='Creds is a library for managing linux user accounts and credentials.',
    # long_description=readme + '\n\n' + history,
    author='Jon Hadfield',
    author_email='jon@lessknown.co.uk',
    url='http://github.com/jonhadfield/creds',
    packages=find_packages('lib'),
    package_dir={'': 'lib'},
    # package_data={'': ['LICENSE', 'NOTICE'], 'creds': ['*.pem']},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),
    cmdclass={'test': PyTest},
    tests_require=test_requirements,
    # extras_require={
    #     'security': [],
    # },
)
