# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

from typing import AnyStr, Optional, List

from creds.users import User


class PublicKey(object):
    def __init__(self, raw: Optional[AnyStr], b64encoded: Optional[AnyStr]) -> None:
        self._raw = raw
        self._b64encoded = b64encoded

    @property
    def b64encoded(self) -> Optional[AnyStr]: pass

    @property
    def raw(self) -> Optional[AnyStr]: pass


# TODO: Keep temporary copy so we can check for race condition.

def read_authorized_keys(username: str) -> List: pass


def write_authorized_keys(user: User) -> List: pass
