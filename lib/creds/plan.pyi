# -*- coding: utf-8 -*-
from typing import List

from creds.users import Users


def create_plan(existing_users: Users, proposed_users: Users, purge_undefined: bool,
                protected_users: List[str],
                allow_non_unique_id: bool, manage_home: bool, manage_keys: bool) -> List: pass


def execute_plan(plan: List[dict]) -> None: pass
