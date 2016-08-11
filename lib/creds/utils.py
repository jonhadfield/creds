# -*- coding: utf-8 -*-
"""This module contains common helper functions."""

from __future__ import unicode_literals

import base64
import os
import random
import string
import subprocess
import sys
import platform

from creds.constants import (SUPPORTED_PLATFORMS, CMD_SUDO)
from external.six import (PY2, PY3)


def sudo_check():
    """Return the string 'sudo' if current user isn't root."""
    sudo_cmd = ''
    if os.geteuid() != 0:
        sudo_cmd = CMD_SUDO
    return sudo_cmd

def get_platform():
    """Return platform name"""
    return platform.system()

def check_platform():
    """Return an error if this is being used on unsupported platform."""
    if not platform.system() in SUPPORTED_PLATFORMS:
        sys.exit('Linux and FreeBSD are currently the only supported platform for this library.')


def execute_command(command=None):
    """Execute a command and return the stdout and stderr."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate()


def random_string(length=10):
    """Generate a random string of ASCII characters."""
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                   for _ in range(length))


def base64encode(_input=None):
    """Return base64 encoded representation of a string."""
    if PY2:  # pragma: no cover
        return base64.b64encode(_input)
    elif PY3:  # pragma: no cover
        if isinstance(_input, bytes):
            return base64.b64encode(_input).decode('UTF-8')
        elif isinstance(_input, str):
            return base64.b64encode(bytearray(_input, encoding='UTF-8')).decode('UTF-8')


def base64decode(_input=None):
    """Take a base64 encoded string and return the decoded string."""
    missing_padding = 4 - len(_input) % 4
    if missing_padding:
        _input += '=' * missing_padding
    if PY2:  # pragma: no cover
        return base64.decodestring(_input)
    elif PY3:  # pragma: no cover
        if isinstance(_input, bytes):
            return base64.b64decode(_input).decode('UTF-8')
        elif isinstance(_input, str):
            return base64.b64decode(bytearray(_input, encoding='UTF-8')).decode('UTF-8')
