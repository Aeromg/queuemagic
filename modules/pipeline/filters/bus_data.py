# -*- coding: utf-8 -*-
from pipelines.filter import Filter

__author__ = 'vdv'


class BusData(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        self._lambda = self.config.strict('lambda', can_call=True)

    def test(self):
        return self._lambda(self.bus.data)