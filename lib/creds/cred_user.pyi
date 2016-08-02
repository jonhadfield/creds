# -*- coding: utf-8 -*-
from typing import Any, List

from creds.ssh import PublicKey


class User(object):
    def __init__(self, name: str, passwd: str, uid: int, gid: int, gecos: str, home_dir: str, shell: str,
                 public_keys: List[PublicKey]): pass

    def gecos(self) -> str: pass

    @staticmethod
    def format_val(val: Any) -> Any: pass
