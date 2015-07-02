# -*- coding: utf-8 -*-
from pipelines.expression_argument import ExpressionArgument
from pipelines.stage import Stage

__author__ = 'vdv'


class BusInteract(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        self._vars = {}
        for key in self.config.keys():
            if key in ['module', 'filter']:
                continue

            self._vars[key] = self.config.get(key=key)

    def execute(self):
        argument = ExpressionArgument(self.bus)

        for key in self._vars.keys():
            value = self._vars[key]
            data = value(argument) if callable(value) else value

            self.bus.append_module_data(self, key=key, data=data)

        return True

    @property
    def is_interfere(self):
        return False