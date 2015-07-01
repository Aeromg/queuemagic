# -*- coding: utf-8 -*-
from pipelines.filter import Filter

__author__ = 'vdv'


class Bypass(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        self._result = self.config.strict('value', default=True, types=[bool])

    def test(self):
        return self._result