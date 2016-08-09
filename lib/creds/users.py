# -*- coding: utf-8 -*-
""" DOC STRING FOR THE MODULE. """
from __future__ import (unicode_literals, print_function)

import io
import json
import os
import shlex

import yaml

from creds.constants import UID_MAX, UID_MIN
from creds.ssh import PublicKey
from creds.ssh import read_authorized_keys
from creds.utils import check_platform
from external.six import text_type


class Users(object):
    """ This is the users class and needs documenting.
    """

    def __init__(self, input_list=None):
        """
        Some words about __init__
        :param input_list: List
        """
        check_platform()
        self.user_list = input_list

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        user_list = ['{0}'.format(user) for user in self.user_list]
        output = '\n'.join(user_list)
        return output

    def add(self, users=None):
        """ Some docstring. """
        self.user_list.extend(users)

    def remove(self, username=None):
        """ Some docstring. """
        self.user_list = [user for user in self.user_list if user.name != username]

    def describe_users(self, users_filter=None):
        """ Some docstring. """
        user_list = list()
        for user in self.user_list:
            if users_filter:
                if users_filter.get('name') == user.name or users_filter.get('uid') == user.uid:
                    public_keys = read_authorized_keys(username=user.name)
                    if public_keys:
                        user.public_keys = public_keys
                    user_list.append(user)
        return user_list

    @classmethod
    def from_dict(cls, input_dict=None):
        """ Some docstring. """
        input_list = list()
        for user_dict in input_dict.get('users'):
            public_keys = None
            if user_dict.get('public_keys'):
                public_keys = [PublicKey(b64encoded=x) for x in user_dict.get('public_keys')]
            input_list.append(User(name=user_dict.get('name'),
                                   passwd=user_dict.get('passwd'),
                                   uid=user_dict.get('uid'),
                                   gid=user_dict.get('gid'),
                                   home_dir=user_dict.get('home_dir'),
                                   gecos=user_dict.get('gecos'),
                                   shell=user_dict.get('shell'),
                                   public_keys=public_keys))
        return cls(input_list=input_list)

    @classmethod
    def from_yaml(cls, file_loc=None):
        """ Some docstring. """
        with io.open(file_loc, encoding=text_type('utf-8')) as stream:
            users_yaml = yaml.safe_load(stream)
            if isinstance(users_yaml, dict):
                input_list = list()
                for user_dict in users_yaml.get('users'):
                    public_keys = None
                    if user_dict.get('public_keys'):
                        public_keys = [PublicKey(b64encoded=x) for x in user_dict.get('public_keys')]
                    input_list.append(User(name=user_dict.get('name'),
                                           passwd=user_dict.get('passwd'),
                                           uid=user_dict.get('uid'),
                                           gid=user_dict.get('gid'),
                                           home_dir=user_dict.get('home_dir'),
                                           gecos=user_dict.get('gecos'),
                                           shell=user_dict.get('shell'),
                                           public_keys=public_keys))
                return cls(input_list=input_list)
            else:
                raise ValueError('No YAML object could be decoded')

    @classmethod
    def from_json(cls, file_loc=None):
        """ Some docstring. """
        with io.open(file_loc, encoding=text_type('utf-8')) as stream:
            try:
                users_json = json.load(stream)
            except ValueError:
                raise
            input_list = list()
            for user_dict in users_json.get('users'):
                public_keys = None
                if user_dict.get('public_keys'):
                    public_keys = [PublicKey(b64encoded=x) for x in user_dict.get('public_keys')]
                input_list.append(User(name=user_dict.get('name'),
                                       passwd=user_dict.get('passwd'),
                                       uid=user_dict.get('uid'),
                                       gid=user_dict.get('gid'),
                                       home_dir=user_dict.get('home_dir'),
                                       gecos=user_dict.get('gecos'),
                                       shell=user_dict.get('shell'),
                                       public_keys=public_keys))
            return cls(input_list=input_list)

    @classmethod
    def from_passwd(cls, uid_min=None, uid_max=None):
        """ Some docstring. """
        import pwd
        input_list = list()
        passwd_list = pwd.getpwall()
        if not uid_min:
            uid_min = UID_MIN
        if not uid_max:
            uid_max = UID_MAX
        for pwd_entry in passwd_list:
            if uid_min <= pwd_entry.pw_uid <= uid_max:
                user = User(name=text_type(pwd_entry.pw_name), passwd=text_type(pwd_entry.pw_passwd),
                            uid=pwd_entry.pw_uid,
                            gid=pwd_entry.pw_gid,
                            gecos=text_type(pwd_entry.pw_gecos),
                            home_dir=text_type(pwd_entry.pw_dir),
                            shell=text_type(pwd_entry.pw_shell),
                            public_keys=read_authorized_keys(username=pwd_entry.pw_name))
                input_list.append(user)
        return cls(input_list=input_list)


class User(object):
    """ Representation of a user and their related credentials. """

    def __init__(self, name=None, passwd=None, uid=None, gid=None, gecos=None,
                 home_dir=None, shell=None, public_keys=None):
        """ Make a user.

        Kwargs:
            name (str): user name.
            passwd (str): password
            uid (int): user id
            gid (int): group id
            gecos (str): GECOS field
            home_dir (str): home directory
            shell (str): shell
            public_keys (list): list of public key instances
        """
        check_platform()
        self.name = name
        self.passwd = passwd
        self.uid = uid
        self.gid = gid
        self._gecos = gecos
        self.home_dir = home_dir
        self.shell = shell
        self.public_keys = public_keys

    @property
    def gecos(self):
        """ Force double quoted gecos.

        returns:
            str: The double quoted gecos.
        """
        if self._gecos.startswith(text_type('\'')) and self._gecos.endswith(text_type('\'')):
            self._gecos = '\"{0}\"'.format(self._gecos[1:-1])
            return self._gecos
        elif self._gecos.startswith(text_type('\"')) and self._gecos.endswith(text_type('\"')):
            return self._gecos
        else:
            return '\"{0}\"'.format(self._gecos)

    def __str__(self):
        return self.__repr__()

    # TODO: Fix - it's nasty
    @staticmethod
    def format_val(val=None):
        """ Double quote string, otherwise return as is.

        args:
            val: something bad

        returns:
            str: something badder
        """
        if val:
            if isinstance(val, text_type):
                return "\"{0}\"".format(val)
            else:
                return val

    def __repr__(self):
        return ("User(name=\"{0}\", passwd={1}, uid={2}, gid={3}, "
                "gecos={4}, home_dir={5}, shell={6}, keys={7})"
                "".format(self.name, self.passwd,
                          self.uid,
                          self.format_val(self.gid),
                          self.gecos,
                          self.format_val(self.home_dir),
                          self.format_val(self.shell),
                          self.format_val(self.public_keys
                                          )))


# TODO: Detect based on OS
USERMOD = '/usr/sbin/usermod'
USERADD = '/usr/sbin/useradd'
USERDEL = '/usr/sbin/userdel'
SUDO = ''
if os.geteuid() != 0:
    SUDO = '/usr/bin/sudo'


def generate_add_user_command(proposed_user=None):
    """ some docstring. """
    command = '{0} {1}'.format(SUDO, USERADD)
    if proposed_user.uid:
        command = '{0} -u {1}'.format(command, proposed_user.uid)
    if proposed_user.gid:
        command = '{0} -g {1}'.format(command, proposed_user.gid)
    if proposed_user.gecos:
        command = '{0} -c \'{1}\''.format(command, proposed_user.gecos)
    if proposed_user.home_dir:
        command = '{0} -d {1}'.format(command, proposed_user.home_dir)
    else:
        command = '{0} -m'.format(command)
    if proposed_user.shell:
        command = '{0} -s {1}'.format(command, proposed_user.shell)
    command = '{0} {1}'.format(command, proposed_user.name)
    return shlex.split(str(command))


def generate_modify_user_command(task=None):
    """ some docstring. """
    name = task['proposed_user'].name
    comparison_result = task['user_comparison']['result']
    command = '{0} {1}'.format(SUDO, USERMOD)
    if comparison_result.get('replacement_uid_value'):
        command = '{0} -u {1}'.format(command, comparison_result.get('replacement_uid_value'))
    if comparison_result.get('replacement_gid_value'):
        command = '{0} -g {1}'.format(command, comparison_result.get('replacement_gid_value'))
    if comparison_result.get('replacement_gecos_value'):
        command = '{0} -c {1}'.format(command, comparison_result.get('replacement_gecos_value'))
    if comparison_result.get('replacement_shell_value'):
        command = '{0} -s {1}'.format(command, comparison_result.get('replacement_shell_value'))
    if comparison_result.get('replacement_home_dir_value'):
        command = '{0} -d {1}'.format(command, comparison_result.get('replacement_home_dir_value'))
    command = '{0} {1}'.format(command, name)
    return shlex.split(str(command))


def generate_delete_user_command(username=None):
    """ some docstring. """
    command = '{0} {1} -r {2}'.format(SUDO, USERDEL, username)
    return shlex.split(str(command))


def get_user_by_uid(uid=None, user_list=None):
    """ some docstring. """
    return user_list.describe_users(users_filter=dict(uid=uid))


def compare_user(passed_user=None, user_list=None):
    """ Check user against existing list """
    # Check if user exists
    returned = user_list.describe_users(users_filter=dict(name=passed_user.name))
    replace_keys = False
    # User exists, so compare attributes
    comparison_result = dict()
    if passed_user.uid and (not returned[0].uid == passed_user.uid):
        comparison_result['uid_action'] = 'modify'
        comparison_result['current_uid_value'] = returned[0].uid
        comparison_result['replacement_uid_value'] = passed_user.uid
    if passed_user.gid and (not returned[0].gid == passed_user.gid):
        comparison_result['gid_action'] = 'modify'
        comparison_result['current_gid_value'] = returned[0].gid
        comparison_result['replacement_gid_value'] = passed_user.gid
    if passed_user.gecos and (not returned[0].gecos == passed_user.gecos):
        comparison_result['gecos_action'] = 'modify'
        comparison_result['current_gecos_value'] = returned[0].gecos
        comparison_result['replacement_gecos_value'] = passed_user.gecos
    if passed_user.home_dir and (not returned[0].home_dir == passed_user.home_dir):
        comparison_result['home_dir_action'] = 'modify'
        comparison_result['current_home_dir_value'] = returned[0].home_dir
        comparison_result['replacement_home_dir_value'] = passed_user.home_dir
        # (Re)set keys if home dir changed
        replace_keys = True
    if passed_user.shell and (not returned[0].shell == passed_user.shell):
        comparison_result['shell_action'] = 'modify'
        comparison_result['current_shell_value'] = returned[0].shell
        comparison_result['replacement_shell_value'] = passed_user.shell
    # if passed_user.public_keys and (not returned[0].public_keys == passed_user.public_keys):
    existing_keys = returned[0].public_keys
    passed_keys = passed_user.public_keys
    # Check if existing and passed keys exist, and if so, compare
    if all((existing_keys, passed_keys)) and len(existing_keys) == len(passed_user.public_keys):
        # Compare each key, and if any differences, replace
        existing = set(key.raw for key in existing_keys)
        replacement = set(key.raw for key in passed_keys)
        if set.difference(existing, replacement):
            replace_keys = True
    # If not existing keys but keys passed set, then
    elif passed_keys and not existing_keys:
        replace_keys = True
    if replace_keys:
        comparison_result['public_keys_action'] = 'modify'
        comparison_result['current_public_keys_value'] = existing_keys
        comparison_result['replacement_public_keys_value'] = passed_keys
    return dict(state='existing', result=comparison_result, existing_user=returned)
