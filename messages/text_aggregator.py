# -*- coding: utf-8 -*-
from messages.payload_proxy import EmailPayloadProxy

__author__ = 'vdv'

from messages.text_proxy import EmailTextContentProxy
from utils.iterable import first_or_default


class EmailTextContentAggregator(EmailPayloadProxy):
    def __init__(self, payload):
        EmailPayloadProxy.__init__(self, payload=payload)

    def get_plain_text_body(self):
        expression = \
            lambda p: \
                (not p.is_multipart()) \
                    and p.get_filename() is None \
                    and p.get_content_maintype() == 'text' \
                    and p.get_content_subtype() == 'plain'

        payload = first_or_default(self.find_payloads(expression))

        if payload:
            return EmailTextContentProxy(payload)

        return None

    def get_html_body(self):
        expression = \
            lambda p: \
                (not p.is_multipart()) \
                    and p.get_filename() is None \
                    and p.get_content_maintype() == 'text' \
                    and p.get_content_subtype() == 'html'

        payload = first_or_default(self.find_payloads(expression))

        if payload:
            return EmailTextContentProxy(payload)

        return None