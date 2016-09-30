# -*- coding: utf-8 -*-
from typing import List, Dict, AnyStr, Optional, Any, Type
from typing import TypeVar, Generic

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


T = TypeVar('T')

U = TypeVar('U', bound=User)


class Users(Generic[T]):
    def __init__(self, oktypes: Optional[Type[U]]) -> None:
        self._user_list = list()
        self.oktypes = oktypes

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

    @classmethod
    def from_passwd(cls, uid_min: int, uid_max: int) -> List: pass

    @staticmethod
    def construct_user_list(raw_users: dict) -> Generic[T]: pass


def generate_add_user_command(proposed_user: User) -> List[str]: pass


def generate_modify_user_command(task: dict) -> List[str]: pass
