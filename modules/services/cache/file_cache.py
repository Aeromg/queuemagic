# -*- coding: utf-8 -*-
from services.base.cache import Cache
from app.logger import log_error

__author__ = 'vdv'

import cPickle as _Pickle
import os
import time


class FileCache(Cache):
    def __init__(self, config, service_resolver):
        Cache.__init__(self, config=config, service_resolver=service_resolver)

        self._cache_prefix = self.config.strict('prefix', types=[str], default='cache')
        self._cache_path = self.config.strict('path', types=[str], non_empty=True)
        self._cache_ttl = self.config.strict('ttl', types=[int], non_empty=True)

    def _get_object_filename(self, key):
        file_name = '{0}_{1}.pkl'.format(self._cache_prefix, key)
        return os.path.join(self._cache_path, file_name)

    @staticmethod
    def _restore_object(filename):
        with open(filename, 'rb') as fh:
            return _Pickle.load(fh)

    @staticmethod
    def _store_object(obj, filename):
        with open(filename, 'wb') as fh:
            return _Pickle.dump(obj, fh, 2)

    def try_get(self, key):
        filename = self._get_object_filename(key)

        if not os.path.exists(filename):
            return None

        lifetime = time.time() - os.stat(filename).st_ctime
        if lifetime <= self._cache_ttl:
            try:
                return FileCache._restore_object(filename)
            except Exception, e:
                log_error(text='File cache restore error', error=e)

        return None

    def set(self, obj, key):
        filename = self._get_object_filename(key)

        if os.path.isfile(filename):
            try:
                os.remove(filename)
            except IOError, e:
                log_error(text='File cache set error', error=e)

        if not os.path.isdir(self._cache_path):
            try:
                os.makedirs(self._cache_path)
            except IOError, e:
                log_error(text='File cache set error', error=e)

        try:
            FileCache._store_object(obj, filename)
        except Exception, e:
            log_error(text='File cache set error', error=e)