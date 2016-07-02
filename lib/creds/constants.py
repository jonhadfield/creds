# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

PURGE_UNDEFINED = False  # Purge any users that fall between UID_MIN and UID_MAX that are not defined

import os

DEFAULT_UID_MIN = 1000  # The lowest uid to consider safe to manage
DEFAULT_UID_MAX = 60000  # The maximum uid to consider safe to manage

def login_defs():
    uid_min = None
    uid_max = None
    if os.path.exists('/etc/login.defs'):
        with open('/etc/login.defs') as f:
            login_data = f.readlines()
        for line in login_data:
            if line.startswith('UID_MIN'):
                uid_min = int(line.split()[1].strip())
            if line.startswith('UID_MAX'):
                uid_max = int(line.split()[1].strip())
    if not uid_min:
        uid_min = DEFAULT_UID_MIN
    if not uid_max:
        uid_max = DEFAULT_UID_MAX
    return uid_min, uid_max


UID_MIN, UID_MAX = login_defs()
ALLOW_NON_UNIQUE_ID = False  # Allow multiple users to share uids
PROTECTED_USERS = list()  # Users that must not be affected
