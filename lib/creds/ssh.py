# -*- coding: utf-8 -*-
"""A class to represent a users' keys and functions to manage them."""
from __future__ import (unicode_literals, print_function)

import os
import shlex

from creds.constants import RANDOM_FILE_EXT_LENGTH
from creds.utils import base64decode, base64encode
from creds.utils import execute_command, random_string, sudo_check
from external.six import text_type


class PublicKey(object):

    """Representation of a public key."""

    def __init__(self, raw=None, b64encoded=None):
        """Make a public key.

        args:
            raw (str): raw public key
            b64encoded (str): base64 encoded public key
        """
        if not any((raw, b64encoded)):
            raise AttributeError('Key not provided')
        self._raw = raw
        self._b64encoded = b64encoded

    @property
    def b64encoded(self):
        """Return a base64 encoding of the key.

        returns:
            str: base64 encoding of the public key
        """
        if self._b64encoded:
            return text_type(self._b64encoded).strip("\r\n")
        else:
            return base64encode(self.raw)

    @property
    def raw(self):
        """Return raw key.

        returns:
            str: raw key
        """
        if self._raw:
            return text_type(self._raw).strip("\r\n")
        else:
            return text_type(base64decode(self._b64encoded)).strip("\r\n")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'PublicKey(raw=\"{0}\", b64encoded=\"{1}\"'.format(self.raw, self.b64encoded)


# TODO: Keep temporary copy so we can check for race condition.

def read_authorized_keys(username=None):
    """Read public keys from specified user's authorized_keys file.

    args:
        username (str): username.

    returns:
        list: Authorised keys for the specified user.
    """
    authorized_keys_path = '{0}/.ssh/authorized_keys'.format(os.path.expanduser('~{0}'.format(username)))
    rnd_chars = random_string(length=RANDOM_FILE_EXT_LENGTH)
    tmp_authorized_keys_path = '/tmp/authorized_keys_{0}_{1}'.format(username, rnd_chars)
    authorized_keys = list()
    copy_result = execute_command(
        shlex.split(str('{0} cp {1} {2}'.format(sudo_check(), authorized_keys_path, tmp_authorized_keys_path))))
    result_message = copy_result[0][1].decode('UTF-8')
    if 'you must have a tty to run sudo' in result_message:  # pragma: no cover
        raise OSError("/etc/sudoers is blocked sudo. Remove entry: 'Defaults    requiretty'.")
    elif 'No such file or directory' not in result_message:
        execute_command(shlex.split(str('{0} chmod 755 {1}'.format(sudo_check(), tmp_authorized_keys_path))))
        with open(tmp_authorized_keys_path) as keys_file:
            for key in keys_file:
                authorized_keys.append(PublicKey(raw=key))
        execute_command(shlex.split(str('{0} rm {1}'.format(sudo_check(), tmp_authorized_keys_path))))
    return authorized_keys


def write_authorized_keys(user=None):
    """Write public keys back to authorized_keys file. Create keys directory if it doesn't already exist.

    args:
        user (User): Instance of User containing keys.

    returns:
        list: Authorised keys for the specified user.
    """
    authorized_keys = list()
    authorized_keys_dir = '{0}/.ssh'.format(os.path.expanduser('~{0}'.format(user.name)))
    rnd_chars = random_string(length=RANDOM_FILE_EXT_LENGTH)
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

