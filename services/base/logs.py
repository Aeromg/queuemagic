# -*- coding: utf-8 -*-
import inspect
import traceback

from services.service import Service


__author__ = 'vdv'


class Logs(Service):
    class Level(object):
        ERROR = 1
        WARN = 2
        INFO = 3
        DEBUG = 4

        @staticmethod
        def parse(text):
            text_l = text.lower()
            return {
                'error': Logs.Level.ERROR,
                'warn': Logs.Level.WARN,
                'info': Logs.Level.INFO,
                'debug': Logs.Level.DEBUG
            }[text_l]

    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    @staticmethod
    def _get_caller(stack_back=3):
        (frame, filename, line_number, function_name, lines, index) = inspect.getouterframes(
            inspect.currentframe())[stack_back]

        return filename, line_number, function_name

    @property
    def log_level(self):
        raise Exception('Method must be overridden')

    def write(self, text):
        raise Exception('Method must be overridden')

    def error(self, text, error, *args):
        if self.log_level < Logs.Level.ERROR:
            return

        (filename, line_number, function_name) = self._get_caller()
        record = 'error {0}:{1} in {2}. {3}'.format(filename, line_number, function_name, str(text))
        self.write(record.format(*args) if args else record)
        self.write(traceback.format_exc(error))

    def warning(self, text, error, *args):
        if self.log_level < Logs.Level.WARN:
            return

        (filename, line_number, function_name) = self._get_caller()
        record = 'warning {0}:{1} in {2}. {3}'.format(filename, line_number, function_name, str(text))
        self.write(record.format(*args) if args else record)
        if error:
            self.write(traceback.format_exc(error))

    def info(self, text, *args):
        if self.log_level < Logs.Level.INFO:
            return

        (filename, line_number, function_name) = self._get_caller()
        record = 'info {0}:{1} in {2}. {3}'.format(filename, line_number, function_name, str(text))
        self.write(record.format(*args) if args else record)

    def debug(self, text, *args):
        if self.log_level < Logs.Level.DEBUG:
            return

        (filename, line_number, function_name) = self._get_caller()
        record = 'debug {0}:{1} in {2}. {3}'.format(filename, line_number, function_name, str(text))
        self.write(record.format(*args) if args else record)