# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

import os
import shlex

from creds.ssh.public_key import PublicKey
from creds.utils import execute_command, random_string, sudo_check
from external.six.six import text_type

# TODO: Keep temporary copy so we can check for race condition.

def read_authorized_keys(username=None):
    """ Read public keys from user's authorized_keys file.

        Kwargs:
            username (str): username.
    """
    authorized_keys_path = '{0}/.ssh/authorized_keys'.format(os.path.expanduser('~{0}'.format(username)))
    rnd_chars = random_string()
    tmp_authorized_keys_path = '/tmp/authorized_keys_{0}_{1}'.format(username, rnd_chars)

    copy_result = execute_command(
        shlex.split(str('{0} cp {1} {2}'.format(sudo_check(), authorized_keys_path, tmp_authorized_keys_path))))
    result_message = copy_result[1].decode('UTF-8')
    if 'you must have a tty to run sudo' in result_message:
        raise OSError("/etc/sudoers is blocked sudo. Remove entry: 'Defaults    requiretty'.")
    elif 'No such file or directory' not in result_message:
        execute_command(shlex.split(str('{0} chmod 755 {1}'.format(sudo_check(), tmp_authorized_keys_path))))
        authorized_keys = list()
        with open(tmp_authorized_keys_path) as keys_file:
            for key in keys_file:
                authorized_keys.append(PublicKey(raw=key))
        execute_command(shlex.split(str('{0} rm {1}'.format(sudo_check(), tmp_authorized_keys_path))))
        return authorized_keys


def write_authorized_keys(user=None):
    """ Write public keys back to authorized_keys file.

        Kwargs:
            user (User): user instance.
    """
    authorized_keys = list()
    authorized_keys_dir = '{0}/.ssh'.format(os.path.expanduser('~{0}'.format(user.name)))
    rnd_chars = random_string()
    authorized_keys_path = '{0}/authorized_keys'.format(authorized_keys_dir)
    tmp_authorized_keys_path = '/tmp/authorized_keys_{0}_{1}'.format(user.name, rnd_chars)

    if not os.path.isdir(authorized_keys_dir):
        execute_command(shlex.split(str('{0} mkdir -p {1}'.format(sudo_check(), authorized_keys_dir))))
    for key in user.public_keys:
        authorized_keys.append('{0}\n'.format(key.raw))
    with open(tmp_authorized_keys_path, mode=text_type('w+')) as keys_file:
        keys_file.writelines(authorized_keys)
    execute_command(
        shlex.split(str('{0} cp {1} {2}'.format(sudo_check(), tmp_authorized_keys_path, authorized_keys_path))))
    execute_command(shlex.split(str('{0} chown -R {1} {2}'.format(sudo_check(), user.name, authorized_keys_dir))))
    execute_command(shlex.split(str('{0} chmod 700 {1}'.format(sudo_check(), authorized_keys_dir))))
    execute_command(shlex.split(str('{0} chmod 600 {1}'.format(sudo_check(), authorized_keys_path))))
    execute_command(shlex.split(str('{0} rm {1}'.format(sudo_check(), tmp_authorized_keys_path))))
