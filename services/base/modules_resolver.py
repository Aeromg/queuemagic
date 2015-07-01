# -*- coding: utf-8 -*-
from services.service import Service

__author__ = 'vdv'


class ModulesResolver(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def get_filter_class(self, name):
        raise Exception('Method must be overridden')

    def get_stage_class(self, name):
        raise Exception('Method must be overridden')