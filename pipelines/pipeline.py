# -*- coding: utf-8 -*-
from app.logger import *

__author__ = 'vdv'

from pipelines.stage import Stage


class FailAction:
    Continue = 1
    Rollback = 2
    Drop = 3
    Crash = 4

    def __init__(self):
        raise Exception('Static class init')

    @staticmethod
    def try_parse(string):
        if string == 'continue':
            return FailAction.Continue

        if string == 'rollback':
            return FailAction.Rollback

        if string == 'drop':
            return FailAction.Drop

        if string == 'raise':
            return FailAction.Crash


class Pipeline(Stage):
    def __init__(self, name, config, bus, filter, service_resolver, modules):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        self._fail_action = FailAction.try_parse(self.config.strict('error',
                                                                    default='continue',
                                                                    values=['continue', 'rollback', 'drop', 'raise']))

        assert all(map(lambda x: isinstance(x, Stage), modules))

        self._modules = modules

    @property
    def on_fail(self):
        return self._fail_action

    @property
    def modules(self):
        return self._modules

    def execute(self):
        pipeline_use_snapshot = self.on_fail in [FailAction.Continue, FailAction.Rollback]

        log_debug('Executing pipeline <{0}>; fail_action={1}; pipeline_use_snapshot={2}; email_facade_obj={3}',
                  self.name, str(self._fail_action), str(pipeline_use_snapshot), str(self.bus.email))

        pipeline_run_result = self.bus.append_stage_result(self)

        if not self.filter.get_result():
            pipeline_run_result.run = True
            pipeline_run_result.filter = False
            return True

        if self.bus.is_disposing:
            pipeline_run_result.run = True
            pipeline_run_result.filter = True
            return True

        for module in self.modules:
            # ToDo: remove line bellow
            assert isinstance(module, Stage)

            if self.bus.is_disposing:
                break

            log_debug('Attempt to exec module <{0}> in pipeline <{1}>', module.name, self.name)

            module_run_result = self.bus.append_stage_result(module=module)

            use_snapshots = pipeline_use_snapshot and module.is_interfere

            try:
                if use_snapshots:
                    self.bus.snapshot_push()

                log_debug('Attempt to test filter <{0}> in module <{1}> in pipeline <{2}>',
                          module.filter.name, module.name, self.name)

                module_run_result.filter = module.filter.get_result()

                log_debug('Filter result={0}', module_run_result.filter)

                if module_run_result.filter:
                    log_debug('Executing module <{0}> in pipeline <{1}>', module.name, self.name)
                    module_run_result.run = module.execute()
                else:
                    module_run_result.run = True

            except Exception, e:
                log_warning('Exception when executing module <{0}> in pipeline <{1}>', e, module.name, self.name)

                module_run_result.run = False
                module_run_result.exception = e

                if self.on_fail == FailAction.Crash:
                    raise

            if not module_run_result.result:
                if self.on_fail == FailAction.Continue:
                    self.bus.snapshot_throw()
                    continue
                elif self.on_fail == FailAction.Rollback:
                    self.bus.snapshot_throw_all()
                    break
                elif self.on_fail == FailAction.Drop:
                    self.bus.snapshot_throw_all()
                    break
            else:
                if use_snapshots:
                    self.bus.snapshot_pull()

                    #        if use_snapshots:
                    #            self.bus.snapshot_pull_all()

        pipeline_run_result.run = True
        pipeline_run_result.filter = True

        log_debug('Pipeline <{0}> exit with snapshot version {1}, email_facade_obj={2}',
                  self.name, self.bus.snapshot_version, str(self.bus.email))

        return True

    @property
    def can_fork(self):
        return any(map(lambda m: m.can_fork, self.modules))

    @property
    def is_interfere(self):
        return any(map(lambda m: m.is_interfere, self.modules))