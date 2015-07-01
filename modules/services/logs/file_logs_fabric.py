# -*- coding: utf-8 -*-
from modules.services.db.shelve_dict import ShelveDict
from modules.services.logs.file_logs import FileLogs
from services.service_fabric import ServiceFabric
from app.config_provider import ConfigProvider

__author__ = 'vdv'


class FileLogsFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    def get_service(self, config):
        return FileLogs(config=config, service_resolver=self.service_resolver)