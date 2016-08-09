# -*- coding: utf-8 -*-
from typing import List, Dict, Any
from creds.ssh import PublicKey


class Users(object):
    def __init__(self, input_list: List) -> None:
        self.user_list = None

    def describe_users(self, users_filter: Dict) -> List: pass

    @classmethod
    def from_dict(cls, input_dict: Dict) -> List: pass

    @classmethod
    def from_yaml(cls, file_loc: str) -> List: pass

    @classmethod
    def from_json(cls, file_loc: str) -> List: pass

    @classmethod
    def from_passwd(cls, uid_min: int, uid_max: int) -> List: pass


class User(object):
    def __init__(self, name: str, passwd: str, uid: int, gid: int, gecos: str, home_dir: str, shell: str,
                 public_keys: List[PublicKey]):
        self.name = name
        self.passwd = passwd
        self.uid = uid
        self.gid = gid
        self.gecos = gecos
        self.home_dir = home_dir
        self.shell = shell

    def gecos(self) -> str: pass

    @staticmethod
    def format_val(val: Any) -> Any: pass

def generate_add_user_command(proposed_user: User) -> List[str]: pass


def generate_modify_user_command(task: dict) -> List[str]: pass
