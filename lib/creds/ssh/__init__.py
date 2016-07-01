# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

import os
import shlex

from creds.ssh.public_key import PublicKey
from creds.utils import execute_command, random_string


def read_authorized_keys(username=None):
    # TODO: COPY FILE AS ROOT TO /TMP/ WITH READ PERMS AND READ THAT INSTEAD
    authorized_keys_path = '{0}/.ssh/authorized_keys'.format(os.path.expanduser('~{0}'.format(username)))
    rnd_chars = random_string()
    tmp_authorized_keys_path = '/tmp/authorized_keys_{0}_{1}'.format(username, rnd_chars)
    copy_result = execute_command(
        shlex.split(str('sudo cp {0} {1}'.format(authorized_keys_path, tmp_authorized_keys_path))))
    if 'No such file or directory' not in copy_result[1].decode('UTF-8'):
        execute_command(shlex.split(str('sudo chmod 755 {0}'.format(tmp_authorized_keys_path))))
        authorized_keys = list()
        with open(tmp_authorized_keys_path) as keys_file:
            for key in keys_file:
                authorized_keys.append(PublicKey(raw=key))
        execute_command(shlex.split(str('sudo rm {0}'.format(tmp_authorized_keys_path))))
        return authorized_keys


def write_authorized_keys(user=None):
    authorized_keys = list()
    authorized_keys_dir = '{0}/.ssh'.format(os.path.expanduser('~{0}'.format(user.name)))
    rnd_chars = random_string()
    authorized_keys_path = '{0}/authorized_keys'.format(authorized_keys_dir)
    tmp_authorized_keys_path = '/tmp/authorized_keys_{0}_{1}'.format(user.name, rnd_chars)

    if not os.path.isdir(authorized_keys_dir):
        execute_command(shlex.split(str('sudo mkdir -p {0}'.format(authorized_keys_dir))))
    for key in user.public_keys:
        authorized_keys.append('{0}\n'.format(key.raw))
    with open(tmp_authorized_keys_path, mode='w+') as keys_file:
        keys_file.writelines(authorized_keys)
    execute_command(shlex.split(str('sudo cp {0} {1}'.format(tmp_authorized_keys_path, authorized_keys_path))))
    execute_command(shlex.split(str('sudo chown -R {0} {1}'.format(user.name, authorized_keys_dir))))
    execute_command(shlex.split(str('sudo chmod 700 {0}'.format(authorized_keys_dir))))
    execute_command(shlex.split(str('sudo chmod 600 {0}'.format(authorized_keys_path))))
    execute_command(shlex.split(str('sudo rm {0}'.format(tmp_authorized_keys_path))))
