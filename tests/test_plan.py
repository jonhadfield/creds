# -*- coding: utf-8 -*-

from __future__ import (absolute_import, unicode_literals)

import shlex

from creds.plan import (create_plan, execute_plan)
from creds.users import (Users, User)
from creds.ssh import PublicKey
from creds.utils import (execute_command, sudo_check, get_platform)
from creds.constants import (LINUX_CMD_USERADD, LINUX_CMD_USERMOD, LINUX_CMD_USERDEL,
                             LINUX_CMD_GROUP_ADD, LINUX_CMD_GROUP_DEL, BSD_CMD_PW)
from external.six import text_type
from .sample_data import PUBLIC_KEYS

# TODO: Detect based on OS
USERMOD = '/usr/sbin/usermod'
USERADD = '/usr/sbin/useradd'
USERDEL = '/usr/sbin/userdel'
GROUPADD = '/usr/sbin/groupadd'
GROUPDEL = '/usr/sbin/groupdel'

PLATFORM = get_platform()

def test_users_instance_creation():
    users = Users()
    users.append(
        User(name='rod', uid=1001, gid=1001, gecos='rod comment', home_dir='/home/rod', shell='/bin/sh'))
    users.append(
        User(name='jane', uid=1002, gid=1002, gecos='jane comment', home_dir='/home/jane', shell='/bin/bash'))
    users.append(
        User(name='freddy', uid=1003, gid=1003, gecos='freddy comment', home_dir='/home/freddy', shell='/bin/false'))
    assert len(users) == 3


def test_create_and_execute_plan_to_create_new_user():
    delete_test_user_and_group()
    create_test_group()
    current_users = Users.from_passwd()

    provided_users = Users()

    public_keys = [PublicKey(
        b64encoded=PUBLIC_KEYS[0]['encoded'])]
    provided_users.append(
        User(name='testuserx1234', home_dir='/home/testuserx1234', shell='/bin/false', gid=59999, uid=59999,
             gecos='test user gecos',
             public_keys=public_keys))
    plan = create_plan(existing_users=current_users, proposed_users=provided_users, purge_undefined=True,
                       protected_users=['travis', 'couchdb', 'ubuntu', 'vagrant'])
    assert plan[0]['state'] == 'missing'
    assert plan[0]['proposed_user'].name == "testuserx1234"
    assert plan[0]['proposed_user'].home_dir == "/home/testuserx1234"
    assert plan[0]['proposed_user'].uid == 59999
    assert plan[0]['proposed_user'].gid == 59999
    assert plan[0]['proposed_user'].gecos == '\"test user gecos\"'
    assert plan[0]['proposed_user'].shell == '/bin/false'
    assert type(plan[0]['proposed_user'].public_keys[0].raw) == text_type
    assert plan[0]['proposed_user'].public_keys[0].raw == text_type(PUBLIC_KEYS[0]['raw'])
    execute_plan(plan=plan)

    current_users = Users.from_passwd()
    plan = create_plan(existing_users=current_users, proposed_users=provided_users, purge_undefined=True,
                       protected_users=['travis', 'couchdb', 'ubuntu', 'nginx', 'hadfielj', 'vagrant'])
    assert not plan



def test_create_and_execute_plan_to_create_identical_user():
    delete_test_user_and_group()
    create_test_user()
    current_users = Users.from_passwd()
    provided_users = Users()
    provided_users.append(User(name='testuserx1234', uid=59999, gecos='test user gecos'))
    plan = create_plan(existing_users=current_users, proposed_users=provided_users)
    execute_plan(plan=plan)
    current_users = Users.from_passwd()
    plan = create_plan(existing_users=current_users, proposed_users=provided_users)
    assert not plan
    delete_test_user_and_group()


def test_update_existing_user():
    delete_test_user_and_group()
    create_test_user()
    current_users = Users.from_passwd()
    provided_users = Users()
    raw_public_key = PUBLIC_KEYS[0].get('raw')
    public_key = PublicKey(raw=raw_public_key)
    provided_users.append(
        User(name='testuserx1234', uid=59999, gecos='test user gecos update', home_dir='/tmp/temp',
             public_keys=[public_key]))
    plan = create_plan(existing_users=current_users, proposed_users=provided_users)
    assert plan[0]['action'] == 'update'
    execute_plan(plan)
    current_users = Users.from_passwd()
    new_user = current_users.describe_users(users_filter=dict(name='testuserx1234'))
    assert new_user[0].public_keys[0].raw == raw_public_key
    delete_test_user_and_group()


def test_execute_plan_to_create_new_user_with_clashing_uid():
    """ Create a new user and then attempt to create another user with existing id """
    delete_test_user_and_group()
    current_users = Users.from_passwd()
    provided_users = Users()
    provided_users.append(User(name='testuserx1234', uid=59999, gecos='test user gecos'))
    plan = create_plan(existing_users=current_users, proposed_users=provided_users)
    assert plan[0]['action'] == 'add'
    assert plan[0]['proposed_user'].name == "testuserx1234"
    assert plan[0]['proposed_user'].uid == 59999
    assert plan[0]['proposed_user'].gecos == '\"test user gecos\"'
    execute_plan(plan=plan)
    current_users = Users.from_passwd()
    provided_users = Users()
    provided_users.append(User(name='testuserx12345', uid=59999, gecos='test user gecos'))
    plan = create_plan(existing_users=current_users, proposed_users=provided_users, purge_undefined=True)
    assert plan[0]['error'] == 'uid_clash'
    execute_plan(plan=plan)
    delete_test_user_and_group()


def test_execute_plan_to_update_existing_user():
    """ Create a new user and then attempt to create another user with existing id """
    delete_test_user_and_group()
    create_test_user()
    raw_public_key_2 = PUBLIC_KEYS[1].get('raw')
    public_key_2 = PublicKey(raw=raw_public_key_2)
    current_users = Users.from_passwd()
    provided_users = Users()
    provided_users.append(
        User(name='testuserx1234', uid=59998, gid=1, gecos='test user gecos update',
             shell='/bin/false', public_keys=[public_key_2]))
    plan = create_plan(existing_users=current_users, proposed_users=provided_users)
    assert plan[0]['proposed_user'].gecos == '\"test user gecos update\"'
    execute_plan(plan=plan)
    updated_users = Users.from_passwd()
    updated_user = updated_users.describe_users(users_filter=dict(name='testuserx1234'))
    assert len(updated_user) == 1
    assert updated_user[0].name == 'testuserx1234'
    assert updated_user[0].uid == 59998
    assert updated_user[0].gid == 1
    assert updated_user[0].gecos == '\"test user gecos update\"'
    assert updated_user[0].shell == '/bin/false'
    assert updated_user[0].public_keys[0].raw == text_type(PUBLIC_KEYS[1]['raw'])
    delete_test_user_and_group()


def test_execute_plan_to_update_existing_user_with_multiple_keys():
    """ Create a new user with 2 keys and then replace with a new one """
    create_test_user()
    raw_public_key_1 = PUBLIC_KEYS[0].get('raw')
    public_key_1 = PublicKey(raw=raw_public_key_1)
    raw_public_key_2 = PUBLIC_KEYS[1].get('raw')
    public_key_2 = PublicKey(raw=raw_public_key_2)
    raw_public_key_3 = PUBLIC_KEYS[2].get('raw')
    public_key_3 = PublicKey(raw=raw_public_key_3)
    raw_public_key_4 = PUBLIC_KEYS[3].get('raw')
    public_key_4 = PublicKey(raw=raw_public_key_4)
    current_users = Users.from_passwd()
    provided_users_2 = Users()
    provided_users_2.append(User(name='testuserx1234', uid=59998, gid=1, gecos='test user gecos update',
                             shell='/bin/false', public_keys=[public_key_1, public_key_2]))
    plan = create_plan(existing_users=current_users, proposed_users=provided_users_2)
    execute_plan(plan=plan)
    updated_users = Users.from_passwd()
    updated_user = updated_users.describe_users(users_filter=dict(name='testuserx1234'))
    assert updated_user[0].public_keys[0].raw == text_type(PUBLIC_KEYS[0]['raw'])
    assert updated_user[0].public_keys[1].raw == text_type(PUBLIC_KEYS[1]['raw'])
    # Replace both keys
    current_users = Users.from_passwd()
    provided_users_3 = Users()
    provided_users_3.append(User(name='testuserx1234', uid=59998, gid=1, gecos='test user gecos update',
             shell='/bin/false', public_keys=[public_key_3, public_key_4]))
    plan = create_plan(existing_users=current_users, proposed_users=provided_users_3)
    execute_plan(plan=plan)
    updated_users = Users.from_passwd()
    updated_user = updated_users.describe_users(users_filter=dict(name='testuserx1234'))
    assert updated_user[0].public_keys[0].raw == text_type(PUBLIC_KEYS[2]['raw'])
    assert updated_user[0].public_keys[1].raw == text_type(PUBLIC_KEYS[3]['raw'])
    # Replace one key
    current_users = Users.from_passwd()
    provided_users_4 = Users()
    provided_users_4.append(
        User(name='testuserx1234', uid=59998, gid=1, gecos='test user gecos update',
             shell='/bin/false', public_keys=[public_key_2, public_key_4]))
    plan = create_plan(existing_users=current_users, proposed_users=provided_users_4)
    execute_plan(plan=plan)
    updated_users = Users.from_passwd()
    updated_user = updated_users.describe_users(users_filter=dict(name='testuserx1234'))
    assert updated_user[0].public_keys[0].raw == text_type(PUBLIC_KEYS[1]['raw'])
    assert updated_user[0].public_keys[1].raw == text_type(PUBLIC_KEYS[3]['raw'])
    delete_test_user_and_group()


def delete_test_user_and_group():
    if PLATFORM == 'Linux':
        del_user_command = shlex.split(str('{0} {1} -r -f testuserx1234'.format(sudo_check(), LINUX_CMD_USERDEL)))
        execute_command(command=del_user_command)
    elif PLATFORM == 'OpenBSD':
        del_user_command = shlex.split(str('{0} {1} -r testuserx1234'.format(sudo_check(), LINUX_CMD_USERDEL)))
        execute_command(command=del_user_command)
    elif PLATFORM == 'FreeBSD':
        del_user_command = shlex.split(str('{0} {1} userdel -r -n testuserx1234'.format(sudo_check(), BSD_CMD_PW)))
        execute_command(command=del_user_command)
    if PLATFORM in ('Linux', 'OpenBSD'):
        del_group_command = shlex.split(str('{0} {1} testuserx1234'.format(sudo_check(), GROUPDEL)))
        execute_command(command=del_group_command)
        del_user_ssh_dir_command = shlex.split(str('/bin/rm -rf /tmp/.ssh'))
        execute_command(command=del_user_ssh_dir_command)
    execute_command(command=shlex.split(str('{0} rm -rf /home/testuserx1234'.format(sudo_check()))))


def create_test_user():
    if PLATFORM in ('Linux', 'OpenBSD'):
        command = shlex.split(
            str('{0} {1} -u 59999 -c \"test user gecos\" -m  -s /bin/bash testuserx1234'.format(sudo_check(), LINUX_CMD_USERADD)))
    elif PLATFORM == 'FreeBSD':
        command = shlex.split(
            str('{0} {1} useradd -u 59999 -c \"test user gecos\" -m  -s /bin/bash -n testuserx1234'.format(sudo_check(), BSD_CMD_PW)))
    assert execute_command(command=command)


def create_test_group():
    if PLATFORM in ('Linux', 'OpenBSD'):
        command = shlex.split(
            str('{0} {1} -g 59999 testuserx1234'.format(sudo_check(), LINUX_CMD_GROUP_ADD)))
    elif PLATFORM == 'FreeBSD':
        command = shlex.split(
            str('{0} {1} groupadd -g 59999 -n testuserx1234'.format(sudo_check(), BSD_CMD_PW)))
    assert execute_command(command=command)
