# -*- coding: utf-8 -*-
from pipelines.filter import Filter

__author__ = 'vdv'


class SkeletonFilter(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        self._a = self.config.strict(key='a', types=[int], values=[0, 5, 10, 20], non_empty=True)
        self._b = self.config.strict(key='b', types=[int], values=[0, 5, 10, 20], non_empty=True)

    def test(self):
        return self._a >= self._b