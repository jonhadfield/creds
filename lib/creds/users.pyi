# -*- coding: utf-8 -*-
from typing import List, Dict, AnyStr, Optional, Any

from creds.ssh import PublicKey


class User(object):
    def __init__(self, name: AnyStr, passwd: Optional[AnyStr], uid: Optional[int], gid: Optional[int],
                 gecos: Optional[AnyStr], home_dir: Optional[AnyStr],
                 shell: Optional[AnyStr], public_keys: Optional[List[PublicKey]]) -> None:
        self.name = name
        self.passwd = passwd
        self.uid = uid
        self.gid = gid
        self._gecos = gecos
        self.home_dir = home_dir
        self.shell = shell
        self.public_keys = public_keys

    def gecos(self) -> str: pass


class Users(object):
    def __init__(self, oktypes: Optional[Any]) -> None: pass

    def describe_users(self, users_filter: Dict) -> List: pass

    @classmethod
    def from_dict(cls, input_dict: Dict) -> List: pass

    @classmethod
    def from_yaml(cls, file_loc: str) -> List: pass

    @classmethod
    def from_json(cls, file_loc: str) -> List: pass

    @classmethod
    def from_passwd(cls, uid_min: int, uid_max: int) -> List: pass


def generate_add_user_command(proposed_user: User) -> List[str]: pass


def generate_modify_user_command(task: dict) -> List[str]: pass
