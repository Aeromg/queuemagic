# -*- coding: utf-8 -*-
from services.service import Service

__author__ = 'vdv'


class Statistics(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def get_message_number(self, sender, recipient):
        raise Exception('Method must be overridden')

    def increment_message_number(self, sender, recipient):
        raise Exception('Method must be overridden')

    def reset_message_number(self, sender, recipient=None):
        raise Exception('Method must be overridden')

    def get_last_message_timestamp(self, sender, recipient):
        raise Exception('Method must be overridden')

    def update_last_message_timestamp(self, sender, recipient, timestamp=None):
        raise Exception('Method must be overridden')

    def reset_last_message_timestamp(self, sender, recipient=None):
        raise Exception('Method must be overridden')

    def reset_sender(self, sender):
        self.reset_message_number(sender=sender)
        self.reset_last_message_timestamp(sender=sender)

    def reset(self):
        raise Exception('Method must be overridden')