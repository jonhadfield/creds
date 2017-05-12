# -*- coding: utf-8 -*-

from typing import Tuple, List, Optional, Union


def sudo_check() -> str: pass


def get_platform() -> str: pass


def get_missing_commands(_platform: str) -> List: pass


def execute_command(command: List) -> Tuple: pass


def random_string(length: Optional[int]) -> str: pass


def base64encode(_input: Union[bytes, str]) -> str: pass


def base64decode(_input: Union[bytes, str]) -> str: pass


def remove_sudoers_entry(username=Optional[str]) -> None: pass


def write_sudoers_entry(username=Optional[str], sudoers_entry=Optional[str]) -> None: pass


def read_sudoers() -> List: pass


def get_sudoers_entry(username=Optional[str], sudoers_entries=List) -> str: pass
