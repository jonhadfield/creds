# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

from creds.utils import base64decode, base64encode
from external.six.six import text_type


class PublicKey(object):
    def __init__(self, raw=None, b64encoded=None):
        if not any((raw, b64encoded)):
            raise AttributeError('Key not provided')
        self._raw = raw
        self._b64encoded = b64encoded

    @property
    def b64encoded(self):
        if self._b64encoded:
            return text_type(self._b64encoded).strip("\r\n")
        else:
            return base64encode(self.raw)

    @property
    def raw(self):
        if self._raw:
            return text_type(self._raw).strip("\r\n")
        else:
            return text_type(base64decode(self._b64encoded)).strip("\r\n")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'PublicKey(raw=\"{0}\", b64encoded=\"{1}\"'.format(self.raw, self.b64encoded)
