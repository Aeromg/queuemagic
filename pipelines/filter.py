# -*- coding: utf-8 -*-
from pipelines.module import Module

__author__ = 'vdv'


class Filter(Module):
    def __init__(self, name, config, bus, service_resolver):
        Module.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        self._negation = self.config.strict('negation', default=False, types=[bool])

    @property
    def is_negation(self):
        return self._negation

    def test(self):
        # base filter isn't test anything
        return True

    def get_result(self):
        return self.test() != self.is_negation


class BypassFilter(Filter):
    def __init__(self):
        pass

    @property
    def is_negation(self):
        return False

    def test(self):
        # base filter isn't test anything
        return True

    def name(self):
        return 'bypass'