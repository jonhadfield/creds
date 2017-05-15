# -*- coding: utf-8 -*-
from typing import List, Dict, AnyStr, Optional, Any, MutableSequence

from creds.ssh import PublicKey


class User(object):
    def __init__(self, name: AnyStr, passwd: Optional[AnyStr], uid: Optional[int], gid: Optional[int],
                 gecos: Optional[AnyStr], home_dir: Optional[AnyStr],
                 shell: Optional[AnyStr], public_keys: Optional[List[PublicKey]],
                 sudoers_entry: Optional[AnyStr]) -> None:
        self.name = name
        self.passwd = passwd
        self.uid = uid
        self.gid = gid
        self._gecos = gecos
        self.home_dir = home_dir
        self.shell = shell
        self.public_keys = public_keys
        self.sudoers_entry = sudoers_entry

    def gecos(self) -> str: pass

    def to_dict(self) -> dict: pass


class Users(MutableSequence):
    def __init__(self) -> None:
        self._user_list = list()
        self.oktypes = User

    def describe_users(self, users_filter: Dict) -> List: pass

    def check(self, value: Any) -> None: pass

    def insert(self, index: int, value: User) -> None: pass

    def remove(self, username: str) -> None: pass

    def __iter__(self) -> User: pass

    def __len__(self) -> int: pass

    def __getitem__(self, index: int) -> User: pass

    def __setitem__(self, index: int, value: User) -> None: pass

    def __delitem__(self, index: int) -> None: pass

    @classmethod
    def from_dict(cls, input_dict: Dict) -> List: pass

    @classmethod
    def from_yaml(cls, file_path: str) -> List: pass

    @classmethod
    def from_json(cls, file_path: str) -> List: pass

    @staticmethod
    def from_passwd(uid_min: int, uid_max: int) -> Users: pass

    @staticmethod
    def construct_user_list(raw_users: dict) -> Users: pass


def generate_add_user_command(proposed_user: User, manage_home: bool) -> List[str]: pass


def generate_modify_user_command(task: dict) -> List[str]: pass


def compare_user(passed_user: User, user_list=Users) -> Dict: pass


def get_user_by_uid(uid: int, users: Users) -> Users: pass
