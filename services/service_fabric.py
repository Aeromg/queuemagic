# -*- coding: utf-8 -*-
__author__ = 'vdv'


class ServiceFabric(object):
    def __init__(self, service_resolver):
        from services.resolver import ServiceResolver
        assert isinstance(service_resolver, ServiceResolver)

        self._service_resolver = service_resolver

    def get_service(self, config):
        raise Exception('Method must be overridden')

    @property
    def service_resolver(self):
        return self._service_resolver