# -*- coding: utf-8 -*-
from typing import Tuple, List

UID_MIN: int
UID_MAX: int
SUPPORTED_PLATFORMS: List[str]
RANDOM_FILE_EXT_LENGTH: int
PURGE_UNDEFINED: bool
DEFAULT_UID_MIN: int
DEFAULT_UID_MAX: int
CMD_SUDO: str
LINUX_CMD_USERADD: str
LINUX_CMD_USERMOD: str
LINUX_CMD_USERDEL: str
LINUX_CMD_GROUP_ADD: str
LINUX_CMD_GROUP_DEL: str
LINUX_CMD_VISUDO: str
FREEBSD_CMD_PW: str


def login_defs() -> Tuple: pass
