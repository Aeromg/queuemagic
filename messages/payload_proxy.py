# -*- coding: utf-8 -*-
__author__ = 'vdv'

from email.message import Message


class EmailPayloadProxy(object):
    def __init__(self, payload):
        assert isinstance(payload, Message)

        self._payload = payload

    def _find_payloads_internal(self, expression, payload=None):
        if payload is None:
            payload = self.payload

        assert isinstance(payload, Message)

        if expression(payload):
            yield payload

        for part in payload.get_payload():
            if not isinstance(part, Message):
                continue

            for filtered in self._find_payloads_internal(expression, payload=part):
                yield filtered

    @property
    def is_multipart(self):
        return self.payload.is_multipart()

    @property
    def payload(self):
        return self._payload

    def get_content(self, decode=False):
        return self.payload.get_payload(decode=decode)

    def set_content(self, content, charset=None):
        return self.payload.set_payload(payload=content, charset=charset)

    @property
    def encoding(self):
        if 'Content-Transfer-Encoding' in self.payload.keys():
            return self.payload['Content-Transfer-Encoding']

        return '8bit'

    @encoding.setter
    def encoding(self, encoding):
        if 'Content-Transfer-Encoding' in self.payload.keys():
            self.payload.replace_header('Content-Transfer-Encoding', encoding)
        else:
            self.payload.add_header('Content-Transfer-Encoding', encoding)

    @property
    def is_text(self):
        return self.payload.get_content_maintype() == 'text'

    def find_payloads(self, expression):
        return self._find_payloads_internal(expression)