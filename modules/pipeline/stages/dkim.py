# -*- coding: utf-8 -*-
from pipelines.stage import Stage
from services.base.domain_keys import DomainKeysSigner
__author__ = 'vdv'


class DKIM(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

    def execute(self):
        email = self.bus.email
        dkim_svc = self.service_resolver.get_service(DomainKeysSigner)
        assert isinstance(dkim_svc, DomainKeysSigner)

        if email.is_dkim_signed:
            del email.header['DKIM-Signature']

        if not self.config.strict(key='remove', default=False, types=[bool]):
            sign_header_raw = dkim_svc.get_sign(email=email)
            email.header.set_raw('DKIM-Signature', sign_header_raw)

        return True