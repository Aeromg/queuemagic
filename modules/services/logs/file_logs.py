# -*- coding: utf-8 -*-
from services.base.logs import Logs

__author__ = 'vdv'


class FileLogs(Logs):
    def __init__(self, config, service_resolver):
        Logs.__init__(self, config=config, service_resolver=service_resolver)

        self._level = Logs.Level.parse(self.config.strict('level',
                                                          values=['error', 'warn', 'info', 'debug'],
                                                          default='warn'))

        self._file = self.config.strict('file', types=[str], non_empty=True)
        self._newline = self.config.strict('newline', types=[str], default='\r\n')

    @property
    def log_level(self):
        return self._level

    def write(self, text):
        with open(name=self._file, mode='a') as fd:
            fd.write(text)
            fd.write(self._newline)