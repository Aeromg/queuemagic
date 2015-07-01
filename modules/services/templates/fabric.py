# -*- coding: utf-8 -*-
from jinja2 import Environment
import importlib
import inspect

from modules.services.templates.text_factory import TextFactory
from services.service_fabric import ServiceFabric
from app.config_provider import ConfigProvider


__author__ = 'vdv'


class TextFactoryFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    @staticmethod
    def _get_filters(config):
        filters = []
        for module in config.strict('filters', types=[str], can_iterate=True):
            for name, func in inspect.getmembers(importlib.import_module(module), inspect.isfunction):
                if name.startswith('_'):
                    continue

                filters.append((name, func))

        return filters

    def get_service(self, config):
        assert isinstance(config, ConfigProvider)
        environment = Environment()
        for name, filter in TextFactoryFabric._get_filters(config=config):
            environment.filters[name] = filter

        return TextFactory(config=config, service_resolver=self.service_resolver, environment=environment)