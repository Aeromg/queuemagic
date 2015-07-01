# -*- coding: utf-8 -*-
from pipelines.bus import Bus

__author__ = 'vdv'


class ExpressionArgument(object):
    def __init__(self, bus):
        assert isinstance(bus, Bus)
        self._bus = bus

    @property
    def email(self):
        return self._bus.email

    @property
    def data(self):
        return self._bus.data

    @property
    def modules(self):
        return self._bus.modules

    @property
    def auth(self):
        return self._bus.auth

    @property
    def is_alien(self):
        return self.auth is None

    @property
    def bus(self):
        return self._bus