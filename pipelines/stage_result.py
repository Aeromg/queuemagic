# -*- coding: utf-8 -*-
__author__ = 'vdv'


class StageResult(object):
    def __init__(self, module):
        from pipelines.module import Module
        assert isinstance(module, Module)

        self._module = module
        self._run = None
        self._filter = None
        self._exception = None

    @property
    def module(self):
        return self._module

    @property
    def run(self):
        return self._run

    @run.setter
    def run(self, value):
        self._run = value

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, value):
        self._filter = value

    @property
    def exception(self):
        return self._exception

    @exception.setter
    def exception(self, value):
        self._exception = value

    @property
    def result(self):
        return self.run or not self.filter

    def __repr__(self):
        return repr(self.get_dict())

    def get_dict(self):
        if self.result and self.filter:
            text = 'pass'
        elif not self.run and self.filter:
            text = 'fail'
        else:
            text = 'skip'

        if self.exception:
            return {self.module.name: {'result': text, 'exception': self.exception}}
        else:
            return {self.module.name: {'result': text}}