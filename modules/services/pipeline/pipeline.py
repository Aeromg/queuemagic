# -*- coding: utf-8 -*-
from pipelines.filter import Filter
from pipelines.pipeline import Pipeline
from services.base.modules_resolver import ModulesResolver

__author__ = 'vdv'

from services.base.pipeline import PipelineService as PipelineServiceBase
from pipelines.bus import Bus


class PipelineService(PipelineServiceBase):
    def __init__(self, config, service_resolver):
        PipelineServiceBase.__init__(self, config=config, service_resolver=service_resolver)
        modules_svc = self.service_resolver.get_service(ModulesResolver)
        assert isinstance(modules_svc, ModulesResolver)
        self._modules_resolver = modules_svc

    def get_state(self, message, data=None):
        """
        :rtype : Bus
        """
        return Bus(email=message, data=data, service_resolver=self._service_resolver)

    def get_filter(self, module_name, bus, config):
        """
        :rtype : Filter
        """
        return self._modules_resolver.get_filter_class(name=module_name)(name=module_name,
                                                                         bus=bus,
                                                                         config=config,
                                                                         service_resolver=self.service_resolver)

    def get_stage(self, module_name, bus, config, filter):
        """
        :rtype : Stage
        """
        return self._modules_resolver.get_stage_class(name=module_name)(name=module_name,
                                                                        config=config,
                                                                        bus=bus,
                                                                        filter=filter,
                                                                        service_resolver=self.service_resolver)

    def get_pipeline(self, name, bus, config, modules, filter):
        """
        :rtype : Pipeline
        """
        return Pipeline(name=name,
                        bus=bus,
                        config=config,
                        filter=filter,
                        service_resolver=self.service_resolver,
                        modules=modules)