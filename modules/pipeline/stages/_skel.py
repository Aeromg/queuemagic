# -*- coding: utf-8 -*-
from pipelines.stage import Stage

__author__ = 'vdv'


class SkeletonStage(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        self._new_subject = self.config.strict(key='new_subject', types=[str, unicode],
                                               default=u'**Subject replaced**', extend=self.bus.data)

    def execute(self):
        self.bus.email.subject = self._new_subject

        return True