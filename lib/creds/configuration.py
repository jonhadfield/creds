# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

from collections import namedtuple

attrs = 'purge_undefined uid_min uid_max allow_non_unique_id protected_users'
CredsConfig = namedtuple('CredsConfig', attrs)
# Safe defaults
config = CredsConfig(purge_undefined=True, uid_min=1000, uid_max=60000, allow_non_unique_id=False,
                     protected_users=list())
