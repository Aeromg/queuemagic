# -*- coding: utf-8 -*-
from services.base.cache import Cache
from services.service_fabric import ServiceFabric
from modules.services.authority.active_directory import ActiveDirectory
from app.config_provider import ConfigProvider

__author__ = 'vdv'


class ActiveDirectoryFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    def get_service(self, config):
        assert isinstance(config, ConfigProvider)

        cache_cfg = config.section('cache') if 'cache' in config.keys() else None
        cache = self.service_resolver.get_service(Cache, config=cache_cfg)

        return ActiveDirectory(config=config, service_resolver=self.service_resolver, cache=cache)