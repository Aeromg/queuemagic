# -*- coding: utf-8 -*-
from pipelines.filter import Filter
from services.base.pipeline import PipelineService

__author__ = 'vdv'


class Aggregation(Filter):
    FILTER_ARGS = ['aggregate', 'negation']

    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        svc = self.service_resolver.get_service(PipelineService)
        assert isinstance(svc, PipelineService)

        self._aggregate = self.config.strict('aggregate', default='all', values=['all', 'any'])

        filters = map(lambda m: svc.get_filter(module_name=m, bus=self.bus, config=config.section(key=m)),
                      [key for key in self.config.keys() if key not in Aggregation.FILTER_ARGS])

        assert all(map(lambda x: isinstance(x, Filter), filters))
        self._filters = filters

    def test(self):
        all_result = True
        for f in self._filters:
            r = f.test() if not f.is_negation else not f.test()
            if self._aggregate == 'any' and r:
                return True

            if self._aggregate == 'all' and not r:
                return False

            all_result = all_result and r

        return all_result