# -*- coding: utf-8 -*-
from modules.services.modules.modules_resolver import ModulesResolver
from services.service_fabric import ServiceFabric

__author__ = 'vdv'


class ModulesResolverFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    def get_service(self, config):
        return ModulesResolver(config=config, service_resolver=self.service_resolver)