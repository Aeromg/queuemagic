# -*- coding: utf-8 -*-
from services.service_fabric import ServiceFabric
from app.config_provider import ConfigProvider
from modules.services.domain_keys.domain_keys import DomainKeysSigner

__author__ = 'vdv'


class DomainKeysSignerFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    def get_service(self, config):
        assert isinstance(config, ConfigProvider)

        return DomainKeysSigner(config=config, service_resolver=self.service_resolver)