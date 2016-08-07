# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

import io
import json

import yaml

from creds.constants import UID_MAX, UID_MIN
from creds.ssh import PublicKey
from creds.ssh import read_authorized_keys
from creds.utils import check_platform
from external.six.six import text_type


class Users(object):
    def __init__(self, input_list=None):
        check_platform()
        self.user_list = input_list

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        user_list = ['{0}'.format(user) for user in self.user_list]
        output = '\n'.join(user_list)
        return output

    def describe_users(self, users_filter=None):
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

        Returns:
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

        Kwargs:
            val: something bad
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
