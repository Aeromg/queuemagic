# -*- coding: utf-8 -*-
from pipelines.stage import Stage
from services.base.statistics import Statistics

__author__ = 'vdv'


class StatisticsFeeder(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

    def execute(self):
        svc = self.service_resolver.get_service(Statistics)
        assert isinstance(svc, Statistics)

        svc.increment_message_number(self.bus.sender, self.bus.recipient)

        return True