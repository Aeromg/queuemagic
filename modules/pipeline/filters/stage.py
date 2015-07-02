# -*- coding: utf-8 -*-
from pipelines.filter import Filter

__author__ = 'vdv'


class Stage(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        self._stage = self.config.strict('stage', types=[str], non_empty=True)
        self._result_in = self.config.strict('result_in', types=[str],
                                             values=['pass', 'skip', 'fail'], can_iterate=True, non_empty=True)

    def test(self):
        modules_run = self.bus.data['modules_run'] if 'modules_run' in self.bus.data.keys() else {}
        for key in modules_run.keys():
            module = modules_run[key]
            module_name = module.keys()[0]
            if module_name != self._stage:
                continue

            if module[module_name]['result'] in self._result_in:
                return True

        return False