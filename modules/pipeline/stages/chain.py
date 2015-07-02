# -*- coding: utf-8 -*-
from pipelines.stage import Stage
from services.base.pipeline import PipelineService

__author__ = 'vdv'


class Chain(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        svc = self.service_resolver.get_service(PipelineService)
        assert isinstance(svc, PipelineService)

        self._pipeline = svc.build_pipeline(name=self.config.strict(key='jump', types=[str], non_empty=True),
                                            bus=self.bus)

    def execute(self):
        result = self._pipeline.execute()
        if not self.config.strict(key='resume', types=[bool], default=True):
            self.bus.dispose()

        return result

    @property
    def can_fork(self):
        return self._pipeline.can_fork

    @property
    def is_interfere(self):
        return False