# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

PURGE_UNDEFINED = False  # Purge any users that fall between UID_MIN and UID_MAX that are not defined

import os
from external.six.six import text_type, PY2, PY3

DEFAULT_UID_MIN = 1000  # The lowest uid to consider safe to manage
DEFAULT_UID_MAX = 60000  # The maximum uid to consider safe to manage


def login_defs():
    uid_min = None
    uid_max = None
    login_defs_path = '/etc/login.defs'
    if os.path.exists(login_defs_path):
        with open(text_type(login_defs_path)) as f:
            login_data = f.readlines()
        for line in login_data:
            if PY3:
                line = str(line)
            if PY2:
                line = line.decode(text_type('UTF-8'))
            if line.startswith(text_type('UID_MIN')):
                uid_min = int(line.split()[1].strip())
            if line.startswith(text_type('UID_MAX')):
                uid_max = int(line.split()[1].strip())
    if not uid_min:
        uid_min = DEFAULT_UID_MIN
    if not uid_max:
        uid_max = DEFAULT_UID_MAX
    return uid_min, uid_max


UID_MIN, UID_MAX = login_defs()
ALLOW_NON_UNIQUE_ID = False  # Allow multiple users to share uids
PROTECTED_USERS = list()  # Users that must not be affected
