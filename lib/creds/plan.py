# -*- coding: utf-8 -*-
""" Functions to generate a list of steps to transition from the current state to the desired state. """
from __future__ import (unicode_literals, print_function)

from creds import constants
from creds.ssh import write_authorized_keys
from creds.users import (generate_add_user_command, generate_modify_user_command,
                         generate_delete_user_command, compare_user, get_user_by_uid)
from creds.utils import execute_command
from external.six import iteritems


def create_plan(existing_users=None, proposed_users=None, purge_undefined=None, protected_users=None,
                allow_non_unique_id=None):
    """ Determine what changes are required

    args:
        existing_users (list): List of discovered users
        proposed_users (list): List of proposed users
        purge_undefined (bool): Whether or not to remove discovered users that have not been defined in proposed users list
        protected_users (list): List of users' names that should not be evaluated as part of the plan creation process
        allow_non_unique_id (bool): Allow more than one user to have the same uid

    returns:
       list: A list of differences between discovered and proposed users with a list of operations that will achieve the desired state.

    """


    plan = list()
    proposed_usernames = list()

    if not purge_undefined:
        purge_undefined = constants.PURGE_UNDEFINED
    if not protected_users:
        protected_users = constants.PROTECTED_USERS
    if not allow_non_unique_id:
        allow_non_unique_id = constants.ALLOW_NON_UNIQUE_ID

    # Create list of modifications to make based on proposed users compared to existing users
    for proposed_user in proposed_users.user_list:
        proposed_usernames.append(proposed_user.name)
        user_matching_name = existing_users.describe_users(users_filter=dict(name=proposed_user.name))
        user_matching_id = get_user_by_uid(uid=proposed_user.uid, user_list=existing_users)
        # If user does not exist
        if not allow_non_unique_id and user_matching_id and not user_matching_name:
            plan.append(
                dict(action='fail', error='uid_clash', proposed_user=proposed_user, state='existing', result=None))
        elif not user_matching_name:
            plan.append(dict(action='add', proposed_user=proposed_user, state='missing', result=None))
        # If they do, then compare
        else:
            user_comparison = compare_user(passed_user=proposed_user, user_list=existing_users)
            if user_comparison.get('result'):
                plan.append(
                    dict(action='update', proposed_user=proposed_user, state='existing',
                         user_comparison=user_comparison))
    # Application of the proposed user list will not result in deletion of users that need to be removed
    # If 'PURGE_UNDEFINED' then look for existing users that are not defined in proposed usernames and mark for removal
    if purge_undefined:
        for existing_user in existing_users.user_list:
            if existing_user.name not in proposed_usernames:
                if existing_user.name not in protected_users:
                    plan.append(dict(action='delete', username=existing_user.name, state='existing'))
    return plan


# TODO: Add 'interactive' option
def execute_plan(plan=None):
    """ Create, Modify or Delete, depending on plan item"""
    execution_result = list()
    for task in plan:
        action = task['action']
        if action == 'delete':
            command = generate_delete_user_command(username=task.get('username'))
            command_output = execute_command(command)
            execution_result.append(dict(task=task, command_output=command_output))
        elif action == 'add':
            command = generate_add_user_command(task.get('proposed_user'))
            command_output = execute_command(command)
            if task['proposed_user'].public_keys:
                write_authorized_keys(task['proposed_user'])
            execution_result.append(dict(task=task, command_output=command_output))
        elif action == 'update':
            result = task['user_comparison'].get('result')
            # Don't modify user if only keys have changed
            action_count = 0
            for k, _ in iteritems(result):
                if '_action' in k:
                    action_count += 1
            command_output = None
            if action_count == 1 and 'public_keys_action' in result:
                write_authorized_keys(task['proposed_user'])
            else:
                command = generate_modify_user_command(task=task)
                command_output = execute_command(command)
                if result.get('public_keys_action'):
                    write_authorized_keys(task['proposed_user'])
            execution_result.append(dict(task=task, command_output=command_output))
