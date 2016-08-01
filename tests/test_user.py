# -*- coding: utf-8 -*-

from __future__ import (absolute_import, unicode_literals, print_function)

from creds.cred_user import User
from creds.ssh.public_key import PublicKey
from tests.sample_data import PUBLIC_KEYS
from creds.utils import sudo_check
import pytest
import os

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
