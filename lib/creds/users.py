# -*- coding: utf-8 -*-
"""This module contains the classes for User (a user's details) and Users (a collection of User instances)."""
from __future__ import unicode_literals

import io
import json
import os
import shlex
import sys
from collections import MutableSequence
from creds.constants import (SUPPORTED_PLATFORMS, UID_MAX, UID_MIN,
                             LINUX_CMD_USERADD, LINUX_CMD_USERDEL, LINUX_CMD_USERMOD,
                             FREEBSD_CMD_PW)
from creds.ssh import PublicKey
from creds.ssh import read_authorized_keys
from creds.utils import (get_platform, sudo_check, read_sudoers, get_sudoers_entry, get_missing_commands)
from external.six import text_type


class User(object):
    """Representation of a user and their related credentials."""

    def __init__(self, name=None, passwd=None, uid=None, gid=None, gecos=None,
                 home_dir=None, shell=None, public_keys=None, sudoers_entry=None):
        """Make a user.

        args:
            name (str): user name.
            passwd (str, optional): password
            uid (int, optional): user id
            gid (int, optional): group id
            gecos (str): GECOS field
            home_dir (str): home directory
            shell (str): shell
            public_keys (list): list of public key instances
            sudoers_entry (str): an entry in sudoers
        """
        self.name = name
        self.passwd = passwd
        self.uid = uid
        self.gid = gid
        self._gecos = gecos
        self.home_dir = home_dir
        self.shell = shell
        self.public_keys = public_keys
        self.sudoers_entry = sudoers_entry

    @property
    def gecos(self):
        """Force double quoted gecos.

        returns:
            str: The double quoted gecos.
        """
        if not self._gecos:
            return None
        if self._gecos.startswith(text_type('\'')) and self._gecos.endswith(text_type('\'')):
            self._gecos = '\"{0}\"'.format(self._gecos[1:-1])
            return self._gecos
        elif self._gecos.startswith(text_type('\"')) and self._gecos.endswith(text_type('\"')):
            return self._gecos
        else:
            return '\"{0}\"'.format(self._gecos)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<User {0}>'.format(self.name)

    def to_dict(self):
        """ Return the user as a dict. """
        public_keys = [public_key.b64encoded for public_key in self.public_keys]
        return dict(name=self.name, passwd=self.passwd, uid=self.uid, gid=self.gid, gecos=self.gecos,
                    home_dir=self.home_dir, shell=self.shell, public_keys=public_keys)


class Users(MutableSequence):
    """A collection of users and methods to manage them."""

    def __init__(self, oktypes=User):
        """Create instance of Users collection.

        args:
            oktypes (type): The acceptable types of instances..
        """
        platform = get_platform()
        # Check platform is supported
        if not platform in SUPPORTED_PLATFORMS:
            sys.exit('Linux, FreeBSD and OpenBSD are currently the only supported platforms for this library.')
        # Check OS commands are available for managing users
        missing_commands = get_missing_commands(platform)
        if missing_commands:
            sys.exit('Unable to find commands: {0}.\nPlease check PATH.'.format(', '.join(missing_commands)))

        self.oktypes = oktypes
        self._user_list = list()

    def check(self, value):
        """Check types."""
        if not isinstance(value, self.oktypes):
            raise TypeError

    def __iter__(self):
        for user in self._user_list:
            yield user

    def __len__(self):
        return len(self._user_list)

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, index):
        return self._user_list[index]

    def insert(self, index, value):
        """Insert an instance of User into the collection."""
        self.check(value)
        self._user_list.insert(index, value)

    def __setitem__(self, index, value):
        self.check(value)
        self._user_list[index] = value

    def __repr__(self):
        user_list = ['{0}'.format(user) for user in self._user_list]
        output = '\n'.join(user_list)
        return output

    def __delitem__(self, index):
        del self._user_list[index]

    def remove(self, username=None):
        """Remove User instance based on supplied user name."""
        self._user_list = [user for user in self._user_list if user.name != username]

    def describe_users(self, users_filter=None):
        """Return a list of users matching a filter (if provided)."""
        user_list = Users(oktypes=User)
        for user in self._user_list:
            if users_filter and (users_filter.get('name') == user.name or users_filter.get('uid') == user.uid):
                user_list.append(user)
        return user_list

    @classmethod
    def from_dict(cls, input_dict=None):
        """Create collection from dictionary content."""
        return cls.construct_user_list(raw_users=input_dict.get('users'))

    @classmethod
    def from_yaml(cls, file_path=None):
        """Create collection from a YAML file."""
        try:
            import yaml
        except ImportError:  # pragma: no cover
            yaml = None
        if not yaml:
            import sys
            sys.exit('PyYAML is not installed, but is required in order to parse YAML files.'
                     '\nTo install, run:\n$ pip install PyYAML\nor visit'
                     ' http://pyyaml.org/wiki/PyYAML for instructions.')

        with io.open(file_path, encoding=text_type('utf-8')) as stream:
            users_yaml = yaml.safe_load(stream)
            if isinstance(users_yaml, dict):
                return cls.construct_user_list(raw_users=users_yaml.get('users'))
            else:
                raise ValueError('No YAML object could be decoded')

    @classmethod
    def from_json(cls, file_path=None):
        """Create collection from a JSON file."""
        with io.open(file_path, encoding=text_type('utf-8')) as stream:
            try:
                users_json = json.load(stream)
            except ValueError:
                raise ValueError('No JSON object could be decoded')
            return cls.construct_user_list(raw_users=users_json.get('users'))

    @staticmethod
    def from_passwd(uid_min=None, uid_max=None):
        """Create collection from locally discovered data, e.g. /etc/passwd."""
        import pwd
        users = Users(oktypes=User)
        passwd_list = pwd.getpwall()
        if not uid_min:
            uid_min = UID_MIN
        if not uid_max:
            uid_max = UID_MAX
        sudoers_entries = read_sudoers()
        for pwd_entry in passwd_list:
            if uid_min <= pwd_entry.pw_uid <= uid_max:
                user = User(name=text_type(pwd_entry.pw_name),
                            passwd=text_type(pwd_entry.pw_passwd),
                            uid=pwd_entry.pw_uid,
                            gid=pwd_entry.pw_gid,
                            gecos=text_type(pwd_entry.pw_gecos),
                            home_dir=text_type(pwd_entry.pw_dir),
                            shell=text_type(pwd_entry.pw_shell),
                            public_keys=read_authorized_keys(username=pwd_entry.pw_name),
                            sudoers_entry=get_sudoers_entry(username=pwd_entry.pw_name,
                                                            sudoers_entries=sudoers_entries))
                users.append(user)
        return users

    @staticmethod
    def construct_user_list(raw_users=None):
        """Construct a list of User objects from a list of dicts."""
        users = Users(oktypes=User)
        for user_dict in raw_users:
            public_keys = None
            if user_dict.get('public_keys'):
                public_keys = [PublicKey(b64encoded=x, raw=None)
                               for x in user_dict.get('public_keys')]
            users.append(User(name=user_dict.get('name'),
                              passwd=user_dict.get('passwd'),
                              uid=user_dict.get('uid'),
                              gid=user_dict.get('gid'),
                              home_dir=user_dict.get('home_dir'),
                              gecos=user_dict.get('gecos'),
                              shell=user_dict.get('shell'),
                              public_keys=public_keys,
                              sudoers_entry=user_dict.get('sudoers_entry')))

        return users

    def to_dict(self):
        """ Return a dict of the users. """
        users = dict(users=list())
        for user in self:
            users['users'].append(user.to_dict())
        return users

    def export(self, file_path=None, export_format=None):
        """ Write the users to a file. """
        with io.open(file_path, mode='w', encoding="utf-8") as export_file:
            if export_format == 'yaml':
                import yaml
                yaml.safe_dump(self.to_dict(), export_file, default_flow_style=False)
            elif export_format == 'json':
                export_file.write(text_type(json.dumps(self.to_dict(), ensure_ascii=False)))
            return True


def generate_add_user_command(proposed_user=None, manage_home=None):
    """Generate command to add a user.

    args:
        proposed_user (User): User
        manage_home: bool

    returns:
        list: The command string split into shell-like syntax
    """
    command = None
    if get_platform() in ('Linux', 'OpenBSD'):
        command = '{0} {1}'.format(sudo_check(), LINUX_CMD_USERADD)
        if proposed_user.uid:
            command = '{0} -u {1}'.format(command, proposed_user.uid)
        if proposed_user.gid:
            command = '{0} -g {1}'.format(command, proposed_user.gid)
        if proposed_user.gecos:
            command = '{0} -c \'{1}\''.format(command, proposed_user.gecos)
        if manage_home:
            if proposed_user.home_dir:
                if os.path.exists(proposed_user.home_dir):
                    command = '{0} -d {1}'.format(command, proposed_user.home_dir)
            elif not os.path.exists('/home/{0}'.format(proposed_user.name)):
                command = '{0} -m'.format(command)
        if proposed_user.shell:
            command = '{0} -s {1}'.format(command, proposed_user.shell)
        command = '{0} {1}'.format(command, proposed_user.name)
    elif get_platform() == 'FreeBSD':  # pragma: FreeBSD
        command = '{0} {1} useradd'.format(sudo_check(), FREEBSD_CMD_PW)
        if proposed_user.uid:
            command = '{0} -u {1}'.format(command, proposed_user.uid)
        if proposed_user.gid:
            command = '{0} -g {1}'.format(command, proposed_user.gid)
        if proposed_user.gecos:
            command = '{0} -c \'{1}\''.format(command, proposed_user.gecos)
        if manage_home:
            if proposed_user.home_dir:
                command = '{0} -d {1}'.format(command, proposed_user.home_dir)
            else:
                command = '{0} -m'.format(command)
        if proposed_user.shell:
            command = '{0} -s {1}'.format(command, proposed_user.shell)
        command = '{0} -n {1}'.format(command, proposed_user.name)

    if command:
        return shlex.split(str(command))


def generate_modify_user_command(task=None, manage_home=None):
    """Generate command to modify existing user to become the proposed user.

    args:
        task (dict): A proposed user and the differences between it and the existing user

    returns:
        list: The command string split into shell-like syntax
    """
    name = task['proposed_user'].name
    comparison_result = task['user_comparison']['result']
    command = None
    if get_platform() in ('Linux', 'OpenBSD'):
        command = '{0} {1}'.format(sudo_check(), LINUX_CMD_USERMOD)
        if comparison_result.get('replacement_uid_value'):
            command = '{0} -u {1}'.format(command, comparison_result.get('replacement_uid_value'))
        if comparison_result.get('replacement_gid_value'):
            command = '{0} -g {1}'.format(command, comparison_result.get('replacement_gid_value'))
        if comparison_result.get('replacement_gecos_value'):
            command = '{0} -c {1}'.format(command, comparison_result.get('replacement_gecos_value'))
        if comparison_result.get('replacement_shell_value'):
            command = '{0} -s {1}'.format(command, comparison_result.get('replacement_shell_value'))
        if manage_home and comparison_result.get('replacement_home_dir_value'):
                command = '{0} -d {1}'.format(command, comparison_result.get('replacement_home_dir_value'))
        command = '{0} {1}'.format(command, name)
    if get_platform() == 'FreeBSD':  # pragma: FreeBSD
        command = '{0} {1} usermod'.format(sudo_check(), FREEBSD_CMD_PW)
        if comparison_result.get('replacement_uid_value'):
            command = '{0} -u {1}'.format(command, comparison_result.get('replacement_uid_value'))
        if comparison_result.get('replacement_gid_value'):
            command = '{0} -g {1}'.format(command, comparison_result.get('replacement_gid_value'))
        if comparison_result.get('replacement_gecos_value'):
            command = '{0} -c {1}'.format(command, comparison_result.get('replacement_gecos_value'))
        if comparison_result.get('replacement_shell_value'):
            command = '{0} -s {1}'.format(command, comparison_result.get('replacement_shell_value'))
        if manage_home and comparison_result.get('replacement_home_dir_value'):
            command = '{0} -d {1}'.format(command, comparison_result.get('replacement_home_dir_value'))
        command = '{0} -n {1}'.format(command, name)
    if command:
        return shlex.split(str(command))


def generate_delete_user_command(username=None, manage_home=None):
    """Generate command to delete a user.

    args:
        username (str): user name
        manage_home (bool): manage home directory

    returns:
        list: The user delete command string split into shell-like syntax
    """
    command = None
    remove_home = '-r' if manage_home else ''

    if get_platform() in ('Linux', 'OpenBSD'):
        command = '{0} {1} {2} {3}'.format(sudo_check(), LINUX_CMD_USERDEL, remove_home, username)
    elif get_platform() == 'FreeBSD':  # pragma: FreeBSD
        command = '{0} {1} userdel {2} -n {3}'.format(sudo_check(), FREEBSD_CMD_PW, remove_home, username)
    if command:
        return shlex.split(str(command))


def get_user_by_uid(uid=None, users=None):
    """Return a list of users, from a supplied list, based on their uid.

    args:
        uid (id): A user id
        user_list (list): An instance of Users

    returns:
        list: a list of users matching the supplied uid
    """
    return users.describe_users(users_filter=dict(uid=uid))


def compare_user(passed_user=None, user_list=None):
    """Check if supplied User instance exists in supplied Users list and, if so, return the differences.

    args:
        passed_user (User): the user instance to check for differences
        user_list (Users): the Users instance containing a list of Users instances

    returns:
        dict: Details of the matching user and a list of differences
    """
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
    if passed_user.sudoers_entry and (not returned[0].sudoers_entry == passed_user.sudoers_entry):
        comparison_result['sudoers_entry_action'] = 'modify'
        comparison_result['current_sudoers_entry'] = returned[0].sudoers_entry
        comparison_result['replacement_sudoers_entry'] = passed_user.sudoers_entry
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
