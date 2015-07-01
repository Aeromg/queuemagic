# -*- coding: utf-8 -*-
from pipelines.stage import Stage
from services.base.authority import AuthoritySource, AuthorityInfo
from services.base.text_factory import TextFactory
import re

__author__ = 'vdv'


class Disclaimer(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        text_svc = self.service_resolver.get_service(TextFactory)
        assert isinstance(text_svc, TextFactory)

        self._text_svc = text_svc

    def _get_text(self, template):
        view_bag = self.config.strict('view_bag', types=[dict], default={}).copy()
        view_bag.update({
            'auth': self.bus.auth,
            'sender': self.bus.sender,
            'recipient': self.bus.recipient,
            'modules': self.bus.modules
        })

        return self._text_svc.get_text(view_bag=view_bag, template=template)

    @staticmethod
    def _append_html(html, text):
        close_tag = re.findall('<\s*/\s*body.*?>', html)
        if len(close_tag) == 0:
            return html

        return html.replace(close_tag[0], text + close_tag[0])

    @staticmethod
    def _append_plain(plain, text):
        return plain + '\n' + text

    def execute(self):
        email = self.bus.email
        if not email.html is None:
            email.html = Disclaimer._append_html(email.html, self._get_text(template=self.config.strict('html')))

        if not email.text is None:
            email.text = Disclaimer._append_plain(email.text, self._get_text(template=self.config.strict('plain')))

        return True