# -*- coding: utf-8 -*-
from pipelines.expression_argument import ExpressionArgument
from pipelines.stage import Stage

__author__ = 'vdv'


class HeaderInject(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        self._header_name = self.config.strict('name', types=[str], non_empty=True)
        self._value = self.config.strict('value', non_empty=True)
        self._allow_replace = self.config.strict('allow_replace', types=[bool], default=True)

    def execute(self):
        headers_proxy = self.bus.email.header

        if self._header_name in headers_proxy.keys() and not self._allow_replace:
            return False

        if callable(self._value):
            headers_proxy.add(self._header_name, self._value(ExpressionArgument(self.bus)))
        else:
            headers_proxy.add(self._header_name, self._value)

        return True