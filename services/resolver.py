# -*- coding: utf-8 -*-
import importlib
import inspect

from app.configurable_module import ConfigurableModule
from services.service_fabric import ServiceFabric


__author__ = 'vdv'


class ServiceResolver(ConfigurableModule):
    def __init__(self, config):
        ConfigurableModule.__init__(self, config=config)

        self._singletons = {}

    def _get_fabric_of_service(self, name):
        location = self.config.section(name).get('fabric').split('.')

        module = '.'.join(location[0:-1])
        module_class = location[-1]

        for class_name, clazz in inspect.getmembers(importlib.import_module(module), inspect.isclass):
            if class_name == module_class:
                return clazz

        raise Exception('No service ' + name)

    def get_service(self, service, config=None):
        service_name = service.__name__
        svc_config = self.config.section(service_name).section('config') if config is None else config
        singleton = self.config.section(service_name).strict('single', types=[bool], default=False)

        if singleton and service_name in self._singletons.keys():
            return self._singletons[service_name]

        fabric = self._get_fabric_of_service(service_name)(service_resolver=self)
        assert isinstance(fabric, ServiceFabric)

        service_instance = fabric.get_service(config=svc_config)
        assert isinstance(service_instance, service)

        if singleton:
            self._singletons[service_name] = service_instance

        return service_instance