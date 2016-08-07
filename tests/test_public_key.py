# -*- coding: utf-8 -*-

from __future__ import (absolute_import, unicode_literals, print_function)

import pytest
from creds.ssh import PublicKey

from .sample_data import PUBLIC_KEYS


def test_invalid_public_key_setup():
    with pytest.raises(AttributeError):
        assert PublicKey()


def test_create_public_key_from_encoded():
    for key in PUBLIC_KEYS:
        public_key = PublicKey(
            b64encoded=key['encoded'])
        assert public_key.raw == key['raw']
        assert public_key.b64encoded == key['encoded']


def test_create_public_key_from_raw():
    for key in PUBLIC_KEYS:
        public_key = PublicKey(raw=key['raw'])
        assert public_key.b64encoded == key['encoded']
        assert public_key.raw == key['raw']


def test_public_key_repr_and_str():
    public_key = PublicKey(raw=PUBLIC_KEYS[0]['raw'])
    assert str(public_key) == public_key.__repr__()
