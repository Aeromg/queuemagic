# -*- coding: utf-8 -*-
from UserDict import UserDict
import shelve
import os

__author__ = 'vdv'

from services.base.db import PersistentDictionary


class ShelveDict(PersistentDictionary):
    def __init__(self, config, service_resolver):
        PersistentDictionary.__init__(self, config=config, service_resolver=service_resolver)

        self._file = self.config.strict('file', types=[str], non_empty=True)
        self._data = shelve.open(self._file)
        self._dispose = False

    def has_key(self, key):
        return self._data.has_key(key=key)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    def delete(self, key):
        del self._data[key]

    def keys(self):
        return self._data.keys()

    def dispose(self):
        if self._dispose:
            return

        self._dispose = True

        try:
            if not self._shelve is None:
                self._shelve.close()
        except:
            pass

    def remove(self):
        self.dispose()
        os.remove(self._file)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.dispose()

    def __del__(self):
        self.dispose()