# -*- coding: utf-8 -*-
from StringIO import StringIO

from pipelines.stage import Stage
from services.base.attachments import Attachments
from services.base.text_factory import TextFactory


__author__ = 'vdv'


class VcardInject(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        self._template = self.config.strict('template', types=[str], non_empty=True)
        self._display = self.config.strict('display', types=[str], non_empty=True)
        self._encoding = self.config.strict('encoding', types=[str], default='cp1251')

        text_svc = self.service_resolver.get_service(TextFactory)
        assert isinstance(text_svc, TextFactory)

        attachment_svc = self.service_resolver.get_service(Attachments)
        assert isinstance(attachment_svc, Attachments)

        self._text_svc = text_svc
        self._attachments_svc = attachment_svc

    def execute(self):
        view_bag = self.config.strict('view_bag', types=[dict], default={}).copy()
        view_bag.update({
            'auth': self.bus.identity,
            'sender': self.bus.sender,
            'recipient': self.bus.recipient,
            'modules': self.bus.modules
        })

        fd = StringIO()
        fd.write(self._text_svc.get_text(view_bag=view_bag, template=self._template).encode(self._encoding))
        fd.seek(0)

        self._attachments_svc.inject_fd(email=self.bus.email, fd=fd, name=self._display)

        return True