# -*- coding: utf-8 -*-
__author__ = 'vdv'

from utils.notify_changed import NotifyChanged
from messages.header_chunk import EmailHeaderChunk


class EmailMessageHeaderProxy(NotifyChanged):
    def __init__(self, name, raw):
        super(EmailMessageHeaderProxy, self).__init__()
        assert isinstance(raw, str)
        assert isinstance(name, str)

        self._name = name
        self._header_chunk = EmailHeaderChunk(raw=raw)

    @property
    def name(self):
        return self._name

    @property
    def raw(self):
        return self._header_chunk.get_raw()

    @raw.setter
    def raw(self, value):
        if self.raw == value:
            return

        self._header_chunk.set_raw(value)
        self.on_changed()

    @property
    def text(self):
        return self._header_chunk.text

    def set_text(self, value):
        if self.text == value:
            return

        self._header_chunk.text = value
        self.on_changed()

    @text.setter
    def text(self, value):
        if value is self.text:
            return

        self._header_chunk.text = value
        self.on_changed()