# -*- coding: utf-8 -*-
from pipelines.expression_argument import ExpressionArgument
from pipelines.stage import Stage
import re
from services.base.sendmail import SendMail

__author__ = 'vdv'


class Copy(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        self._destination = self.config.strict(key='destination', types=[str], default=None)
        self._lambda = self.config.strict(key='lambda', can_call=True, non_empty=False)

        assert bool(self._destination) != bool(self._lambda)
        assert not self._destination is None or not self._lambda is None

    def _write(self, destination):
        with open(name=destination, mode='w') as fd:
            self.bus.email.write_to(fd=fd)

    def _send(self, destination):
        svc = self.service_resolver.get_service(SendMail)
        assert isinstance(svc, SendMail)

        svc.send(self.bus.email, recipients=[destination])

    def execute(self):
        if self._lambda:
            destination = self._lambda(ExpressionArgument(bus=self.bus))
        else:
            destination = self._destination

        if re.match('^[-0-9a-zA-Z.+_]+@[-0-9a-zA-Z.+_]+\.[a-zA-Z]+$', destination):
            self._send(destination)
        else:
            self._write(destination)

        return True