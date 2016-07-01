# -*- coding: utf-8 -*-

from __future__ import (absolute_import, unicode_literals, print_function)

import os

import pytest

from creds.cred_user import User
from creds.cred_users import Users
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
    assert isinstance(users.user_list, list)


def test_get_users_from_dict():
    users = Users.from_dict(input_dict=SAMPLE_DICT)
    assert isinstance(users.user_list, list)
    assert isinstance(users.user_list, list)
    assert isinstance(users.user_list, list)
    assert isinstance(users.user_list[0], User)
    assert isinstance(users.user_list[0].uid, int)


def test_get_users_from_yaml():
    users = Users.from_yaml(file_loc='{0}/yaml_input/basic.yml'.format(os.path.dirname(os.path.abspath(__file__))))
    assert isinstance(users.user_list, list)
    assert isinstance(users.user_list, list)
    assert isinstance(users.user_list[0], User)
    assert isinstance(users.user_list[0].uid, int)
    assert users.user_list[0].name == 'peter'
    assert users.user_list[0].home_dir == '/home/bigal'


def test_get_users_from_json():
    users = Users.from_json(file_loc='{0}/json_input/basic.json'.format(os.path.dirname(os.path.abspath(__file__))))
    assert isinstance(users.user_list, list)
    assert isinstance(users.user_list, list)
    assert isinstance(users.user_list[0], User)
    assert isinstance(users.user_list[0].uid, int)


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


def test_users_filters():
    users = Users(
        input_list=[User(name='rod', uid=1001, gid=1001, gecos='rod comment', home_dir='/home/rod', shell='/bin/sh')])
    assert not users.describe_users(users_filter=dict(name='nobody'))
    assert not users.describe_users(users_filter=dict(uid=1000))
