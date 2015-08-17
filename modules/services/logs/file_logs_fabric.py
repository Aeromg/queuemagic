# -*- coding: utf-8 -*-
from modules.services.logs.file_logs import FileLogs
from services.service_fabric import ServiceFabric

__author__ = 'vdv'


class FileLogsFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    def get_service(self, config):
        return FileLogs(config=config, service_resolver=self.service_resolver)