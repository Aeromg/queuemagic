# -*- coding: utf-8 -*-
import sys
import time
from pipelines.filter import Filter
from services.base.statistics import Statistics as StatisticsSvc

__author__ = 'vdv'


class Statistics(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

    def test(self):
        sender = self.bus.sender
        recipient = self.bus.recipient
        svc = self.service_resolver.get_service(StatisticsSvc)
        assert isinstance(svc, StatisticsSvc)

        first_time = self.config.strict(key='first_time', types=[bool], default=False)
        antiquity = self.config.strict(key='antiquity', types=[int], default=sys.maxint)
        aggregate = self.config.strict('aggregate', default='any', values=['all', 'any'])

        if first_time:
            first_time_ok = svc.get_message_number(sender=sender, recipient=recipient) == 0
        else:
            first_time_ok = True

        timestamp = svc.get_last_message_timestamp(sender=sender, recipient=recipient)
        antiquity_ok = (time.time() - timestamp) > antiquity

        if aggregate == 'all':
            return antiquity_ok and first_time_ok
        else:
            return antiquity_ok or first_time_ok