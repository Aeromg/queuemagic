# -*- coding: utf-8 -*-
from app.configurable_module import ConfigurableModule
from services.resolver import ServiceResolver

__author__ = 'vdv'


class Service(ConfigurableModule):
    def __init__(self, config, service_resolver):
        ConfigurableModule.__init__(self, config=config)
        assert isinstance(service_resolver, ServiceResolver)
        self._service_resolver = service_resolver

    @property
    def service_resolver(self):
        return self._service_resolver