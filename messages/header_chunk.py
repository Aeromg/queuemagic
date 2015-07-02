# -*- coding: utf-8 -*-
__author__ = 'vdv'

from email.header import decode_header, make_header

from utils.notify_changed import NotifyChanged


class EmailHeaderChunk(NotifyChanged):
    def __init__(self, raw=None, decoded=None, charset=None):
        super(EmailHeaderChunk, self).__init__()

        self._raw = None
        self._text = None
        self._charset = charset

        if not raw is None:
            assert decoded is None and charset is None
            assert isinstance(raw, str)

            self._raw = raw

            self._update_from_raw()
        else:
            assert isinstance(decoded, unicode) or isinstance(decoded, str)

            self._charset = charset if charset else 'utf-8'

            if isinstance(decoded, str):
                self._text = unicode(decoded.decode(self._charset))
            else:
                self._text = decoded.decode(self._charset)

            self._update_from_text()

    def _update_from_raw(self):
        (decoded, charset) = decode_header(self.get_raw())[0]
        if charset:
            decoded = decoded.decode(charset)

        self._charset = charset
        self._text = decoded

    def _update_from_text(self):
        try:
            self._raw = make_header([(self._text, self._charset)]).encode()
            return
        except:
            pass
        try:
            self._raw = make_header([(self._text, 'utf-8')]).encode()
            self._charset = 'utf-8'
            return
        except:
            pass
        try:
            self._raw = make_header([(self._text.encode('utf-8', errors='ignore'), 'utf-8')]).encode()
            self._charset = 'utf-8'
            return
        except:
            raise

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        assert isinstance(value, unicode)

        if self.text is value:
            return

        self._text = value
        self._update_from_text()
        self.on_changed()

    def get_raw(self):
        return self._raw

    def set_raw(self, raw):
        if raw == self._raw:
            return

        self._raw = raw
        self._update_from_raw()
        self.on_changed()