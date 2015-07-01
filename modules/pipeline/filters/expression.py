# -*- coding: utf-8 -*-
from pipelines.expression_argument import ExpressionArgument
from pipelines.filter import Filter

__author__ = 'vdv'


class Expression(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        self._expression = self.config.strict('lambda', default=None, can_call=True)
        self._error = self.config.strict('error', default='fail', types=[str], values=['fail', 'pass', 'raise'])

    def test(self):
        if not self._expression is None:
            try:
                return self._expression(ExpressionArgument(self.bus))
            except:
                if self._error == 'raise':
                    raise

                if self._error == 'pass':
                    return True

                if self._error == 'fail':
                    return False

        return True