# -*- coding: utf-8 -*-
from app.config_provider import ConfigProvider

__author__ = 'vdv'


class ConfigurableModule(object):
    def __init__(self, config):
        assert isinstance(config, ConfigProvider)

        self._config = config

    @property
    def config(self):
        return self._config

    def get_config(self, section=None):
        if section is None:
            return self._config

        return self._config.section(section)