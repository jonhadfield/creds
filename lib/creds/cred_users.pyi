# -*- coding: utf-8 -*-
from typing import List, Dict


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
