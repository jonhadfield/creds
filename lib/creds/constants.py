# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

PURGE_UNDEFINED = False   # Purge any users that fall between UID_MIN and UID_MAX that are not defined
UID_MIN = 1000  # The lowest uid to consider safe to manage
UID_MAX = 60000  # The maximum uid to consider safe to manage
ALLOW_NON_UNIQUE_ID = False  # Allow multiple users to share uids
PROTECTED_USERS = list()  # Users that must not be affected