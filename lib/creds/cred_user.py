# -*- coding: utf-8 -*-
""" This module contains class:
User:
A representation of a user entry in a passwd file plus their credentials.
"""
from __future__ import (unicode_literals, print_function)

from creds.utils import check_platform
from external.six.six import text_type


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
                "gecos={4}, home_dir={5}, shell={6}, keys={7})".format(self.name, self.passwd,
                                                                       self.uid,
                                                                       self.format_val(self.gid),
                                                                       self.gecos,
                                                                       self.format_val(self.home_dir),
                                                                       self.format_val(self.shell),
                                                                       self.format_val(self.public_keys
                                                                                       )))
