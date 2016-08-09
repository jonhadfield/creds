# -*- coding: utf-8 -*-

from __future__ import (absolute_import, unicode_literals, print_function)

import os

import pytest

from creds.ssh import PublicKey
from creds.users import (Users, User)
from creds.utils import sudo_check
from tests.sample_data import PUBLIC_KEYS
from .sample_data import SAMPLE_DICT


def test_users_instance_creation():
    input_user_list = list()
    input_user_list.append(
        User(name='rod', uid=1001, gid=1001, gecos='rod comment', home_dir='/home/rod', shell='/bin/sh'))
    input_user_list.append(
        User(name='jane', uid=1002, gid=1002, gecos='jane comment', home_dir='/home/jane', shell='/bin/bash'))
    input_user_list.append(
        User(name='freddy', uid=1003, gid=1003, gecos='freddy comment', home_dir='/home/freddy', shell='/bin/false'))
    assert Users(input_list=input_user_list)


def test_get_users_from_passwd():
    users = Users.from_passwd()
    assert isinstance(users, Users)


def test_get_users_from_dict():
    users = Users.from_dict(input_dict=SAMPLE_DICT)
    assert isinstance(users, Users)
    assert isinstance(users[0], User)
    assert isinstance(users[0].uid, int)


def test_get_users_from_yaml():
    users = Users.from_yaml(file_loc='{0}/yaml_input/basic.yml'.format(os.path.dirname(os.path.abspath(__file__))))
    assert isinstance(users, Users)
    assert isinstance(users[0], User)
    assert isinstance(users[0].uid, int)
    assert users[0].name == 'peter'
    assert users[0].home_dir == '/home/bigal'


def test_get_users_from_json():
    users = Users.from_json(file_loc='{0}/json_input/basic.json'.format(os.path.dirname(os.path.abspath(__file__))))
    assert isinstance(users, Users)
    assert isinstance(users[0], User)
    assert isinstance(users[0].uid, int)


def test_get_users_from_invalid_yaml():
    with pytest.raises(ValueError):
        Users.from_yaml(file_loc='{0}/yaml_input/invalid.yml'.format(os.path.dirname(os.path.abspath(__file__))))


def test_get_users_from_invalid_json():
    with pytest.raises(ValueError):
        Users.from_json(file_loc='{0}/json_input/invalid.json'.format(os.path.dirname(os.path.abspath(__file__))))


def test_users_repr():
    users = Users(
        input_list=[User(name='rod', uid=1001, gid=1001, gecos='rod comment', home_dir='/home/rod', shell='/bin/sh')])
    assert str(users) == users.__repr__()


def test_users_add_and_remove():
    rod = User(name='rod', uid=1001, gid=1001, gecos='rod comment', home_dir='/home/rod', shell='/bin/sh')
    users = Users(
        input_list=[rod])
    assert len(users) == 1
    jane = User(name='jane')
    users.add([jane])
    assert len(users) == 2
    users.remove(username='jane')
    assert len(users) == 1


def test_users_filters():
    users = Users(
        input_list=[User(name='rod', uid=1001, gid=1001, gecos='rod comment', home_dir='/home/rod', shell='/bin/sh')])
    assert not users.describe_users(users_filter=dict(name='nobody'))
    assert not users.describe_users(users_filter=dict(uid=1000))


def test_user_instance_creation():
    name = 'Fred'
    uid = 1024
    gid = 1024
    gecos = 'Fred Bloggs'
    home_dir = '/home/fred'
    shell = '/bin/false'
    public_key = PublicKey(raw=PUBLIC_KEYS[0]['raw'])
    test_user = User(name=name, uid=uid, gid=gid, gecos=gecos, home_dir=home_dir, shell=shell, public_keys=[public_key])
    assert test_user.name == name
    assert test_user.uid == uid
    assert test_user.gid == gid
    # Ensure gecos is surrounded with double quotes
    assert test_user.gecos.startswith('\"') and test_user.gecos.endswith('\"')
    assert test_user.home_dir == home_dir
    assert test_user.shell == shell
    assert test_user.public_keys == [public_key]


def test_user_instance_creation_precommented_gecos():
    name = 'Fred'
    uid = 1024
    gid = 1024
    gecos = '\'Fred Bloggs\''
    home_dir = '/home/fred'
    shell = '/bin/false'
    test_user = User(name=name, uid=uid, gid=gid, gecos=gecos, home_dir=home_dir, shell=shell)
    assert test_user.name == name
    assert test_user.uid == uid
    assert test_user.gid == gid
    # Ensure gecos is surrounded with double quotes
    assert test_user.gecos.startswith('\"') and test_user.gecos.endswith('\"')
    assert test_user.home_dir == home_dir
    assert test_user.shell == shell


def test_user_instance_with_missing_gecos():
    rod = User(name='rod', uid=1001, gid=1001, home_dir='/home/rod', shell='/bin/sh')
    assert rod.gecos == None


def test_platform_detection(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: 'Darwin')
    with pytest.raises(OSError):
        name = 'Fred'
        uid = 1024
        gid = 1024
        gecos = 'Fred Bloggs'
        home_dir = '/home/fred'
        shell = '/bin/false'
        public_key = PublicKey(raw=PUBLIC_KEYS[0]['raw'])
        User(name=name, uid=uid, gid=gid, gecos=gecos, home_dir=home_dir, shell=shell, public_keys=[public_key])


def test_user_detection(monkeypatch):
    monkeypatch.setattr("os.geteuid", lambda: 1)
    assert sudo_check() == 'sudo'
    monkeypatch.setattr("os.geteuid", lambda: 0)
    assert sudo_check() == ''
