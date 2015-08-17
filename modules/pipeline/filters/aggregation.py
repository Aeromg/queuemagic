# -*- coding: utf-8 -*-
from pipelines.filter import Filter
from services.base.pipeline import PipelineService

__author__ = 'vdv'


class Aggregation(Filter):
    FILTER_ARGS = ['aggregate', 'negation', 'module']

    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        svc = self.service_resolver.get_service(PipelineService)
        assert isinstance(svc, PipelineService)

        self._aggregate = self.config.strict('aggregate', default='all', values=['all', 'any'])

        def make_filter(key):
            filter_config = config.section(key=key)
            module_name = filter_config.strict('module', types=[str], non_empty=True) \
                if 'module' in filter_config.keys() else key
            return svc.get_filter(module_name=module_name, bus=self.bus, config=filter_config)

        self._filters = [make_filter(key=key) for key in self.config.keys() if key not in Aggregation.FILTER_ARGS]

    def test(self):
        results = [f.test() ^ f.is_negation for f in self._filters]
        return any(results) if self._aggregate == 'any' else all(results)