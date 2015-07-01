# -*- coding: utf-8 -*-
from pipelines.filter import Filter
from pipelines.stage import Stage
from services.base.modules_resolver import ModulesResolver as ModulesResolverBase

__author__ = 'vdv'

import importlib
import inspect


class ModulesResolver(ModulesResolverBase):
    def __init__(self, config, service_resolver):
        ModulesResolverBase.__init__(self, config=config, service_resolver=service_resolver)

        self._stages = self.config.section('stages')
        self._filters = self.config.section('filters')

    @staticmethod
    def _get_module_path_tuple(path):
        path_arr = path.split('.')
        return '.'.join(path_arr[0:-1]), path_arr[-1]

    @staticmethod
    def _get_module_class(section, name):
        (package, cls) = ModulesResolver._get_module_path_tuple(section.get(name))

        for class_name, clazz in inspect.getmembers(importlib.import_module(package), inspect.isclass):
            if class_name == cls:
                return clazz

        raise Exception('No class {0} in package {1}'.format(cls, package))

    def get_filter_class(self, name):
        return ModulesResolver._get_module_class(section=self._filters, name=name)

    def get_stage_class(self, name):
        return ModulesResolver._get_module_class(section=self._stages, name=name)