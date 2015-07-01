# -*- coding: utf-8 -*-
from app.configurable_module import ConfigurableModule
from services.resolver import ServiceResolver

__author__ = 'vdv'

from pipelines.bus import Bus


class Module(ConfigurableModule):
    def __init__(self, name, config, bus, service_resolver):
        ConfigurableModule.__init__(self, config=config)

        self._name = name

        assert isinstance(bus, Bus)
        self._bus = bus

        assert isinstance(service_resolver, ServiceResolver)
        self._service_resolver = service_resolver

        self._module_meta = None

    @property
    def name(self):
        return self._name

    @property
    def alias(self):
        return self.config.base_key.split('.')[-1]

    @property
    def bus(self):
        return self._bus

    @property
    def service_resolver(self):
        return self._service_resolver