# -*- coding: utf-8 -*-
from services.base.cache import Cache

__author__ = 'vdv'

import cPickle as _Pickle
import os
import time


class FileCache(Cache):
    def __init__(self, config, service_resolver):
        Cache.__init__(self, config=config, service_resolver=service_resolver)

        self._cache_prefix = self.config.strict('prefix', types=[str], non_empty=False)
        self._cache_path = self.config.strict('path', types=[str], non_empty=True)
        self._cache_ttl = self.config.strict('ttl', types=[int], non_empty=True)

    def _get_object_filename(self, key):
        file_name = '{0}_{1}.pkl'.format(self._cache_prefix, key)
        return os.path.join(self._cache_path, file_name)

    @staticmethod
    def _restore_object(filename):
        fh = open(filename, 'rb')
        obj = _Pickle.load(fh)
        fh.close()
        return obj

    @staticmethod
    def _store_object(obj, filename):
        fh = open(filename, 'wb')
        obj = _Pickle.dump(obj, fh, 2)
        fh.close()
        return obj

    def try_get(self, key):
        filename = self._get_object_filename(key)

        if not os.path.exists(filename):
            return None

        lifetime = time.time() - os.stat(filename).st_ctime
        if lifetime <= self._cache_ttl:
            return FileCache._restore_object(filename)

        return None

    def set(self, obj, key):
        filename = self._get_object_filename(key)

        if os.path.exists(filename):
            os.remove(filename)

        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        FileCache._store_object(obj, filename)