# -*- coding: utf-8 -*-
from pipelines.stage import Stage
from services.base.pipeline import PipelineService

__author__ = 'vdv'


class Switch(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        svc = self.service_resolver.get_service(PipelineService)
        assert isinstance(svc, PipelineService)

        self._condition = svc.get_filter(module_name='filter', bus=self.bus, config=self.config.section('if'))

        then_config = self.config.section('then')
        self._then_stage = svc.get_stage(module_name=then_config.strict('module', types=[str], non_empty=True),
                                         bus=self.bus,
                                         config=then_config,
                                         filter=svc.get_stage_filter(bus=self.bus, stage_config=then_config))

        else_config = self.config.section('else')
        self._else_stage = svc.get_stage(module_name=else_config.strict('module', types=[str], non_empty=True),
                                         bus=self.bus,
                                         config=else_config,
                                         filter=svc.get_stage_filter(bus=self.bus, stage_config=else_config))

    def execute(self):
        stage = self._then_stage if self._condition.get_result() else self._else_stage

        result = self.bus.append_stage_result(stage, filter_result=True)
        result.run = stage.execute()

        return result.run

    @property
    def can_fork(self):
        return self._then_stage.can_fork or self._else_stage.can_fork

    @property
    def is_interfere(self):
        return self._then_stage.is_interfere or self._else_stage.is_interfere