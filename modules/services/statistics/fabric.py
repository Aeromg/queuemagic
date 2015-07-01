# -*- coding: utf-8 -*-
from modules.services.statistics.statistics import Statistics
from services.service_fabric import ServiceFabric
from app.config_provider import ConfigProvider

__author__ = 'vdv'


class StatisticsFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    def get_service(self, config):
        assert isinstance(config, ConfigProvider)

        return Statistics(config=config, service_resolver=self.service_resolver)