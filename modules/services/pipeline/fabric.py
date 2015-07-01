# -*- coding: utf-8 -*-
from modules.services.pipeline.pipeline import PipelineService
from services.service_fabric import ServiceFabric

__author__ = 'vdv'


class PipelineServiceFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    def get_service(self, config):
        return PipelineService(config=config, service_resolver=self.service_resolver)