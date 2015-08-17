# -*- coding: utf-8 -*-
from pipelines.stage_result import StageResult
from services.resolver import ServiceResolver
from app.logger import *

__author__ = 'vdv'

from messages.mail import EmailFacade
from messages.snapshot import EmailSnapshotBranch
from services.base.identification import IdentificationSource


class Bus(object):
    def __init__(self, email, data, service_resolver):
        assert isinstance(email, EmailFacade)
        assert isinstance(data, dict)
        assert isinstance(service_resolver, ServiceResolver)

        self._service_resolver = service_resolver
        self._snapshot = EmailSnapshotBranch(email=email)
        self._data = data
        self._modules = {}
        self._is_disposing = False
        self._identity = None
        self._is_authorised = None

    @property
    def user(self):
        return self._data['sasl_username'] if 'sasl_username' in self._data.keys() else self.sender.split('@')[0]

    @property
    def sender(self):
        return self._data['sender'] if 'sender' in self._data.keys() else self._snapshot.email.from_address.address

    @property
    def recipient(self):
        if 'recipient' in self._data.keys():
            return self._data['recipient']
        else:
            return self._snapshot.email.to_addresses[0].address if len(self._snapshot.email.to_addresses) > 0 else None

    @property
    def identity(self):
        """
        :rtype : Identification
        """
        if self._is_authorised is None:
            auth_source = self._service_resolver.get_service(IdentificationSource)
            assert isinstance(auth_source, IdentificationSource)
            info = auth_source.try_get_auth(self.sender)
            self._is_authorised = not info is None
            self._identity = info

        return self._identity

    @property
    def email(self):
        return self._snapshot.email

    @property
    def data(self):
        return self._data

    @property
    def modules(self):
        return self._modules

    def append_module_data(self, module, key, data):
        assert isinstance(key, str)
        assert isinstance(data, dict)

        if module.alias in self.modules.keys():
            module_dict = self.modules[module.alias]
        else:
            module_dict = {}
            self.modules[module.alias] = module_dict

        if key in module_dict.keys():
            module_dict[key].update(data)
        else:
            module_dict[key] = data.copy()

    def append_bus_data(self, key, data):
        self._data[key] = data

    def snapshot_push(self):
        log_debug('Snapshot PUSH from version {0}', self._snapshot.version)
        self._snapshot.push()
        log_debug('Current snapshot version {0}', self._snapshot.version)

    def snapshot_pull(self):
        log_debug('Snapshot PULL from version {0}', self._snapshot.version)
        self._snapshot.pull()
        log_debug('Current snapshot version {0}', self._snapshot.version)

    def snapshot_throw(self):
        log_debug('Snapshot THROW from version {0}', self._snapshot.version)
        self._snapshot.throw()
        log_debug('Current snapshot version {0}', self._snapshot.version)

    def snapshot_pull_all(self):
        log_debug('Snapshot PUSH ALL from version {0}', self._snapshot.version)
        self._snapshot.pull_all()
        log_debug('Current snapshot version {0}', self._snapshot.version)

    def snapshot_throw_all(self):
        log_debug('Snapshot PULL ALL from version {0}', self._snapshot.version)
        self._snapshot.throw_all()
        log_debug('Current snapshot version {0}', self._snapshot.version)

    @property
    def snapshot_version(self):
        return self._snapshot.version

    def append_stage_result(self, module, run=None, filter_result=None):
        run_result = StageResult(module=module)

        if 'modules_run' not in self.data.keys():
            modules_run_section = {}
            self.data['modules_run'] = modules_run_section
        else:
            modules_run_section = self.data['modules_run']

        if not run is None:
            run_result.run = run

        if not filter_result is None:
            run_result.filter = filter_result

        modules_run_section[len(modules_run_section)] = run_result
        return run_result

    @property
    def is_disposing(self):
        return self._is_disposing

    def dispose(self):
        log_debug('Calling pipeline disposing. Previous disposing bus: {0}', self._is_disposing)
        self._is_disposing = True