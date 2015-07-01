# -*- coding: utf-8 -*-
from services.service import Service

__author__ = 'vdv'


class TextFactory(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def get_text(self, view_bag, template):
        raise Exception('Method must be overridden')