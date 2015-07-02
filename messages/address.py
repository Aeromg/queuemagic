# -*- coding: utf-8 -*-
from utils.iterable import first_or_default
from utils.observable_list import ObservableList

__author__ = 'vdv'

from email.utils import formataddr, getaddresses

from utils.notify_changed import NotifyChanged
from messages.header_chunk import EmailHeaderChunk


class EmailAddress(NotifyChanged):
    def __init__(self, raw=None, decoded_name=None, address=None):
        super(EmailAddress, self).__init__()

        if not raw is None:
            assert decoded_name is None and address is None

            if isinstance(raw, tuple):
                raw_str = formataddr(raw)
            elif isinstance(raw, str):
                raw_str = raw
            else:
                raise Exception('')

            self._raw = raw_str
            (encoded_name, address) = getaddresses([raw_str])[0]
            self._name_chunk = EmailHeaderChunk(raw=encoded_name)
            self._address = address
        else:
            assert not address is None
            if decoded_name is None:
                decoded_name = ''

            self._name_chunk = EmailHeaderChunk(decoded=u'')
            self._name_chunk.text = decoded_name
            self._address = address

    @property
    def name(self):
        return self._name_chunk.text

    @name.setter
    def name(self, value):
        if isinstance(value, unicode):
            self._name_chunk.text = value
        else:
            self._name_chunk.text = unicode(value.decode('utf-8'))

        self.on_changed()

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

        self.on_changed()

    def format(self):
        return formataddr((self._name_chunk.get_raw(), self.address))

    def __repr__(self):
        if self.name:
            return '"{0}" <{1}>'.encode('utf-8').format(self.name.encode('utf-8'),
                                                        unicode(self.address.encode('utf-8')))
        else:
            return '<{0}>'.encode('utf-8').format(unicode(self.address.encode('utf-8')))


class EmailAddresses(ObservableList):
    def __init__(self, value, observer=None):
        ObservableList.__init__(self, value=value, observer=observer)

    def append_address(self, address, name):
        self.append(EmailAddress(address=address, decoded_name=name))

    def remove_address(self, address):
        address_obj = first_or_default([obj for obj in self if obj.address == address])
        if address_obj:
            self.remove(address_obj)