# -*- coding: utf-8 -*-
from modules.services.cache.file_cache import FileCache
from services.service_fabric import ServiceFabric
from app.config_provider import ConfigProvider

__author__ = 'vdv'


class FileCacheFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    def get_service(self, config):
        assert isinstance(config, ConfigProvider)

        return FileCache(config=config, service_resolver=self.service_resolver)