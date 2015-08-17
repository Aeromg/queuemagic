# -*- coding: utf-8 -*-
from pipelines.filter import Filter

__author__ = 'vdv'


class AttachmentFilter(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

    def test(self):
        email = self.bus.email

        return True