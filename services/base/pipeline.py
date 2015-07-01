# -*- coding: utf-8 -*-
from pipelines.filter import BypassFilter
from pipelines.module import Module
from services.service import Service

__author__ = 'vdv'


class PipelineService(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def get_module_name(self, module):
        assert isinstance(module, Module)

        return module.__class__.__name__

    def get_state(self, message, data=None):
        """
        :rtype : bus
        """
        raise Exception('Method must be overridden')

    def get_filter(self, module_name, bus, config):
        """
        :rtype : Filter
        """
        raise Exception('Method must be overridden')

    def get_stage(self, module_name, bus, config, filter):
        """
        :rtype : Stage
        """
        raise Exception('Method must be overridden')

    def get_pipeline(self, name, bus, config, modules, filter):
        """
        :rtype : Pipeline
        """
        raise Exception('Method must be overridden')

    def build_pipeline(self, name, bus=None, message=None, data=None):
        if bus is None:
            assert not message is None and not data is None
        else:
            assert message is None and data is None

        pipeline_state = self.get_state(message=message, data=data) if bus is None else bus

        pipeline_config = self.config.section(name)

        modules = []
        for stage_name in pipeline_config.strict('queue', types=[str], can_iterate=True, non_empty=False):
            module_config = pipeline_config.section('stages').section(stage_name)
            module_name = module_config.strict(key='module', types=[str], default=stage_name)
            stage = self.get_stage(module_name=module_name,
                                   bus=pipeline_state,
                                   config=module_config,
                                   filter=self.get_stage_filter(bus=pipeline_state, stage_config=module_config))
            modules.append(stage)

        pipeline = self.get_pipeline(name=name,
                                     bus=pipeline_state,
                                     config=pipeline_config,
                                     modules=modules,
                                     filter=self.get_stage_filter(bus=pipeline_state, stage_config=pipeline_config))

        return pipeline

    def get_stage_filter(self, bus, stage_config):
        if 'filter' in stage_config.keys():
            return self.get_filter(module_name='filter', bus=bus, config=stage_config.section('filter'))
        else:
            return BypassFilter()