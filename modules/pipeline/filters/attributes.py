# -*- coding: utf-8 -*-
import sys

from pipelines.filter import Filter


__author__ = 'vdv'


class Attributes(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        self._with_referenced = self.config.strict('with_referenced', default=True, types=[bool])
        self._max_size = self.config.strict('max_size', default=sys.maxint, types=[int])
        self._min_size = self.config.strict('min_size', default=0, types=[int])

    def test(self):
        referenced_test_ok = True
        if not self._with_referenced:
            referenced_test_ok = not self.bus.email.is_referenced

        size_test_ok = self._min_size <= self.bus.email.size <= self._max_size

        return referenced_test_ok and size_test_ok