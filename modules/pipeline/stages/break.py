# -*- coding: utf-8 -*-
from pipelines.stage import Stage

__author__ = 'vdv'


class Break(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

    def execute(self):
        self.bus.dispose()

        return True