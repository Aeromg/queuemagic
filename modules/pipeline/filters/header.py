# -*- coding: utf-8 -*-
from pipelines.filter import Filter
import re
__author__ = 'vdv'


class Header(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        self._header = self.config.strict('name', types=[str], non_empty=True)
        self._pattern = self.config.strict('pattern', types=[str], non_empty=True)
        self._miss_ok = self.config.strict('miss_ok', types=[bool], default=False)

    def test(self):
        headers_proxy = self.bus.email.header
        if self._header not in headers_proxy.keys():
            return self._miss_ok

        return len(re.findall(self._pattern, headers_proxy[self._header],
                              re.UNICODE + re.MULTILINE + re.IGNORECASE)) > 0