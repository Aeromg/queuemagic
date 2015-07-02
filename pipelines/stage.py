# -*- coding: utf-8 -*-
from pipelines.filter import Filter
from pipelines.module import Module

__author__ = 'vdv'


class Stage(Module):
    def __init__(self, name, config, bus, filter, service_resolver):
        Module.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)
        assert isinstance(filter, Filter)
        self._filter = filter

    @property
    def filter(self):
        return self._filter

    def execute(self):
        # base module isn't do anything
        return True

    @property
    def can_fork(self):
        return False

    @property
    def is_interfere(self):
        return True