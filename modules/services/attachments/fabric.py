# -*- coding: utf-8 -*-
from modules.services.attachments.injector import AttachmentInjector
from services.service_fabric import ServiceFabric

__author__ = 'vdv'


class AttachmentsFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    def get_service(self, config):
        return AttachmentInjector(config=config, service_resolver=self.service_resolver)