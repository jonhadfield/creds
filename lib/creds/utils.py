# -*- coding: utf-8 -*-
"""This module contains common helper functions."""

from __future__ import unicode_literals

import base64
import os
import platform
import random
import shlex
import string
import subprocess

from creds.constants import (CMD_SUDO, RANDOM_FILE_EXT_LENGTH, LINUX_CMD_GROUP_ADD, LINUX_CMD_GROUP_DEL,
                             LINUX_CMD_USERADD, LINUX_CMD_USERDEL, LINUX_CMD_USERMOD, FREEBSD_CMD_PW, LINUX_CMD_VISUDO)
from external.six import (PY2, PY3, text_type)


def sudo_check():
    """Return the string 'sudo' if current user isn't root."""
    sudo_cmd = ''
    if os.geteuid() != 0:
        sudo_cmd = CMD_SUDO
    return sudo_cmd


def get_platform():
    """Return platform name"""
    return platform.system()


def get_missing_commands(_platform):
    """Check I can identify the necessary commands for managing users."""
    missing = list()
    if _platform in ('Linux', 'OpenBSD'):
        if not LINUX_CMD_USERADD:
            missing.append('useradd')
        if not LINUX_CMD_USERMOD:
            missing.append('usermod')
        if not LINUX_CMD_USERDEL:
            missing.append('userdel')
        if not LINUX_CMD_GROUP_ADD:
            missing.append('groupadd')
        if not LINUX_CMD_GROUP_DEL:
            missing.append('groupdel')
    elif _platform == 'FreeBSD':  # pragma: FreeBSD
        # FREEBSD COMMANDS
        if not FREEBSD_CMD_PW:
            missing.append('pw')
    if missing:
        print('\nMISSING = {0}'.format(missing))
    return missing


def execute_command(command=None):
    """Execute a command and return the stdout and stderr."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stdin = process.communicate()
    process.wait()
    return (stdout, stdin), process.returncode


def random_string(length=None):
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


def read_sudoers():
    """ Read the sudoers entry for the specified user.

    args:
        username (str): username.

    returns:`r
        str: sudoers entry for the specified user.
    """
    sudoers_path = '/etc/sudoers'
    rnd_chars = random_string(length=RANDOM_FILE_EXT_LENGTH)
    tmp_sudoers_path = '/tmp/sudoers_{0}'.format(rnd_chars)
    sudoers_entries = list()
    copy_result = execute_command(
        shlex.split(str('{0} cp {1} {2}'.format(sudo_check(), sudoers_path, tmp_sudoers_path))))
    result_message = copy_result[0][1].decode('UTF-8')
    if 'No such file or directory' not in result_message:
        execute_command(shlex.split(str('{0} chmod 755 {1}'.format(sudo_check(), tmp_sudoers_path))))
        with open(tmp_sudoers_path) as tmp_sudoers_file:
            for line in tmp_sudoers_file:
                stripped = line.strip().replace(os.linesep, '')
                if stripped and not stripped.startswith('#'):
                    sudoers_entries.append(stripped)
        execute_command(shlex.split(str('{0} rm {1}'.format(sudo_check(), tmp_sudoers_path))))
    return sudoers_entries


def write_sudoers_entry(username=None, sudoers_entry=None):
    """Write sudoers entry.

    args:
        user (User): Instance of User containing sudoers entry.

    returns:
        str: sudoers entry for the specified user.
    """

    sudoers_path = '/etc/sudoers'
    rnd_chars = random_string(length=RANDOM_FILE_EXT_LENGTH)
    tmp_sudoers_path = '/tmp/sudoers_{0}'.format(rnd_chars)
    execute_command(
        shlex.split(str('{0} cp {1} {2}'.format(sudo_check(), sudoers_path, tmp_sudoers_path))))
    execute_command(
        shlex.split(str('{0} chmod 777 {1}'.format(sudo_check(), tmp_sudoers_path))))
    with open(tmp_sudoers_path, mode=text_type('r')) as tmp_sudoers_file:
        sudoers_entries = tmp_sudoers_file.readlines()
    sudoers_output = list()
    for entry in sudoers_entries:
        if entry and not entry.startswith(username):
            sudoers_output.append(entry)
    if sudoers_entry:
        sudoers_output.append('{0} {1}'.format(username, sudoers_entry))
        sudoers_output.append('\n')
    with open(tmp_sudoers_path, mode=text_type('w+')) as tmp_sudoers_file:
        tmp_sudoers_file.writelines(sudoers_output)
    sudoers_check_result = execute_command(
        shlex.split(str('{0} {1} -cf {2}'.format(sudo_check(), LINUX_CMD_VISUDO, tmp_sudoers_path))))
    if sudoers_check_result[1] > 0:
        raise ValueError(sudoers_check_result[0][1])
    execute_command(
        shlex.split(str('{0} cp {1} {2}'.format(sudo_check(), tmp_sudoers_path, sudoers_path))))
    execute_command(shlex.split(str('{0} chown root:root {1}'.format(sudo_check(), sudoers_path))))
    execute_command(shlex.split(str('{0} chmod 440 {1}'.format(sudo_check(), sudoers_path))))
    execute_command(shlex.split(str('{0} rm {1}'.format(sudo_check(), tmp_sudoers_path))))


def remove_sudoers_entry(username=None):
    """Remove sudoers entry.

    args:
        user (User): Instance of User containing sudoers entry.

    returns:
        str: sudoers entry for the specified user.
    """
    sudoers_path = '/etc/sudoers'
    rnd_chars = random_string(length=RANDOM_FILE_EXT_LENGTH)
    tmp_sudoers_path = '/tmp/sudoers_{0}'.format(rnd_chars)
    execute_command(
        shlex.split(str('{0} cp {1} {2}'.format(sudo_check(), sudoers_path, tmp_sudoers_path))))
    execute_command(
        shlex.split(str('{0} chmod 777 {1}'.format(sudo_check(), tmp_sudoers_path))))
    with open(tmp_sudoers_path, mode=text_type('r')) as tmp_sudoers_file:
        sudoers_entries = tmp_sudoers_file.readlines()
    sudoers_output = list()
    for entry in sudoers_entries:
        if not entry.startswith(username):
            sudoers_output.append(entry)
    with open(tmp_sudoers_path, mode=text_type('w+')) as tmp_sudoers_file:
        tmp_sudoers_file.writelines(sudoers_output)
    execute_command(
        shlex.split(str('{0} cp {1} {2}'.format(sudo_check(), tmp_sudoers_path, sudoers_path))))
    execute_command(shlex.split(str('{0} chown root:root {1}'.format(sudo_check(), sudoers_path))))
    execute_command(shlex.split(str('{0} chmod 440 {1}'.format(sudo_check(), sudoers_path))))
    execute_command(shlex.split(str('{0} rm {1}'.format(sudo_check(), tmp_sudoers_path))))


def get_sudoers_entry(username=None, sudoers_entries=None):
    """ Find the sudoers entry in the sudoers file for the specified user.

    args:
        username (str): username.
        sudoers_entries (list): list of lines from the sudoers file.

    returns:`r
        str: sudoers entry for the specified user.
    """
    for entry in sudoers_entries:
        if entry.startswith(username):
            return entry.replace(username, '').strip()
