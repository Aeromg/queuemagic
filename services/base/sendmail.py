# -*- coding: utf-8 -*-
from messages.mail import EmailFacade
from services.service import Service

__author__ = 'vdv'


class SendMail(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def send(self, email, recipients=None, sender=None):
        raise Exception('Method must be overridden')