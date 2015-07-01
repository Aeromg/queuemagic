# -*- coding: utf-8 -*-
from modules.services.sendmail.postfix_sendmail import PostfixSendMail
from services.service_fabric import ServiceFabric
__author__ = 'vdv'


class PostfixSendMailFabric(ServiceFabric):
    def __init__(self, service_resolver):
        ServiceFabric.__init__(self, service_resolver=service_resolver)

    def get_service(self, config):
        return PostfixSendMail(config=config, service_resolver=self.service_resolver)