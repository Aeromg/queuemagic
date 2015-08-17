# -*- coding: utf-8 -*-
__author__ = 'vdv'

import base64
import quopri

from messages.payload_proxy import EmailPayloadProxy


def _get_encoder_by_selector(selector):
    if not selector:
        selector = '8bit'

    selector_l = selector.lower()

    if selector_l == 'quoted-printable':
        return quopri.encodestring

    if selector_l == 'base64':
        return base64.encodestring

    return lambda x: x


class EmailTextContentProxy(EmailPayloadProxy):
    def __init__(self, payload):
        EmailPayloadProxy.__init__(self, payload=payload)

        assert not self.is_multipart
        assert self.is_text

    @staticmethod
    def _try_encode(text, charset, errors='strict'):
        try:
            return text.encode(charset, errors=errors)
        except:
            return None

    @property
    def charset(self):
        charset = self.payload.get_content_charset()
        if not charset:
            return 'ascii'

        return charset

    def get_text(self):
        charset = self.charset
        if charset is None:
            return self.get_content(decode=True)

        decoded = self.get_content(decode=True)
        try:
            return unicode(decoded.decode(charset))
        except:
            try:
                return unicode(decoded.decode(charset, errors='ignore'))
            except:
                return unicode(decoded)

    def set_text(self, text):
        charset = self.charset
        encoding = self.encoding

        if isinstance(text, str):
            text = unicode(text.decode('utf-8'))

        encoded = self._try_encode(text, charset)
        if not encoded:
            encoded = self._try_encode(text, 'utf-8')
            charset = 'utf-8'

        if not encoded:
            encoded = self._try_encode(text, 'utf-8', 'ignore')
            charset = 'utf-8'

        encode_changed = False
        if charset != 'ascii' and (encoding is None or encoding.lower() in ['7bit', '8bit']):
            encoding = 'quoted-printable'
            encode_changed = True

        if encoding:
            encoded = _get_encoder_by_selector(encoding)(encoded)

        if encode_changed:
            self.encoding = encoding

        self.payload.set_charset(charset)
        self.set_content(encoded)