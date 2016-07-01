# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, print_function)

import base64
import random
import string
import subprocess

from external.six import six


def execute_command(command=None):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate()


def random_string(length=10):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


def base64encode(_input=None):
    if six.PY2:
        return base64.b64encode(_input)
    elif six.PY3:
        if isinstance(_input, bytes):
            return base64.b64encode(_input).decode('UTF-8')
        elif isinstance(_input, str):
            return base64.b64encode(bytearray(_input, encoding='UTF-8')).decode('UTF-8')


def base64decode(_input=None):
    missing_padding = 4 - len(_input) % 4
    if missing_padding:
        _input += '=' * missing_padding
    if six.PY2:
        return base64.decodestring(_input)
    elif six.PY3:
        if isinstance(_input, bytes):
            return base64.b64decode(_input).decode('UTF-8')
        elif isinstance(_input, str):
            return base64.b64decode(bytearray(_input, encoding='UTF-8')).decode('UTF-8')
