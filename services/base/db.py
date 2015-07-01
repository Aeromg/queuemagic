# -*- coding: utf-8 -*-
from services.service import Service

__author__ = 'vdv'


class PersistentDictionary(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def has_key(self, key):
        raise Exception('Method must be overridden')

    def get(self, key, default=None):
        raise Exception('Method must be overridden')

    def set(self, key, value):
        raise Exception('Method must be overridden')

    def delete(self, key):
        raise Exception('Method must be overridden')

    def keys(self):
        raise Exception('Method must be overridden')

    def remove(self):
        raise Exception('Method must be overridden')