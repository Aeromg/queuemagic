# -*- coding: utf-8 -*-
__author__ = 'vdv'

from email.utils import getaddresses
from email.message import Message

from messages.address import EmailAddress, EmailAddresses
from messages.header_proxy import EmailMessageHeaderProxy


class EmailHeadersAggregator(object):
    ADDRESS_HEADERS = ['From', 'Reply-To', 'Delivered-To', 'Return-Path']
    ADDRESSES_HEADERS = ['To', 'cc', 'bcc']
    SPECIAL_HEADERS = ADDRESS_HEADERS + ADDRESSES_HEADERS

    def __init__(self, message):
        assert isinstance(message, Message)

        self._header_proxies = {}
        self._message = message

    def contains(self, name):
        return name in self.keys()

    def create_header_proxy(self, name, value=None):
        self.set_raw(name, '' if value is None else value)
        if name in EmailHeadersAggregator.SPECIAL_HEADERS:
            return self[name]
        else:
            proxy = self.get_header_proxy(name)
            if value:
                proxy.text = value

        return proxy

    def get_header_proxy(self, name):
        if name in self._header_proxies.keys():
            return self._header_proxies[name]

        def header_changed(header_proxy):
            self.set_raw(header_proxy.name, header_proxy.raw)

        proxy = EmailMessageHeaderProxy(name=name, raw=''.join(self.get_all(name)))
        self._header_proxies[name] = proxy

        proxy.changed.append(header_changed)

        return proxy

    def del_header_proxy(self, name):
        if name in self._header_proxies.keys():
            del self._header_proxies[name]

        del self._message[name]

    def get_all(self, name):
        return self._message.get_all(name)

    def get_raw(self, name):
        return self._message.get(name)

    def set_raw(self, name, value):
        if name in self._message.keys():
            self._message.replace_header(name, value)
        else:
            self._message.add_header(name, value)

    def del_raw(self, name):
        del self._message[name]

    def _get_addresses_header_proxy_list(self, header_name):
        if header_name in self._header_proxies.keys():
            return self._header_proxies[header_name]

        proxy = EmailAddresses(
            map(lambda raw: EmailAddress(raw=raw), getaddresses(self.get_all(header_name)))
            if header_name in self._message.keys() else []
        )

        self._header_proxies[header_name] = proxy

        def address_changed(address):
            proxy.on_changed()

        def addresses_changed(addresses):
            value = ', \r\n\t'.join(map(lambda a: a.format(), addresses))
            if header_name in self._message.keys():
                self._message.replace_header(header_name, value)
            else:
                self._message.add_header(header_name, value)
            for a in addresses:
                if not address_changed in a.changed:
                    a.changed.append(address_changed)

        proxy.changed.append(addresses_changed)

        for address in proxy:
            address.changed.append(address_changed)

        return proxy

    def _get_address_header_proxy(self, header_name):
        if header_name in self._header_proxies.keys():
            return self._header_proxies[header_name]

        if header_name in self._message.keys():
            proxy = EmailAddress(raw=self.get_all(header_name)[0])
        else:
            proxy = EmailAddress(decoded_name=u'', address=u'')

        def address_changed(address):
            if header_name in self._message.keys():
                self._message.replace_header(header_name, address.format())
            else:
                self._message.add_header(header_name, address.format())

        proxy.changed.append(address_changed)

        return proxy

    def _set(self, header, value):
        if header in EmailHeadersAggregator.SPECIAL_HEADERS:
            return

        if header in self._message.keys():
            self.get_header_proxy(header).text = value
        else:
            self.create_header_proxy(header).text = value

    def _get(self, header):
        if header in EmailHeadersAggregator.ADDRESS_HEADERS:
            return self._get_address_header_proxy(header)

        if header in EmailHeadersAggregator.ADDRESSES_HEADERS:
            return self._get_addresses_header_proxy_list(header)

        return self.get_header_proxy(header).text

    def _del(self, header):
        if header in self._message.keys():
            del self._message[header]
            self.del_header_proxy(header)
        else:
            raise KeyError()

    def __setitem__(self, key, item):
        self._set(header=key, value=item)

    def __getitem__(self, key):
        return self._get(header=key)

    def __repr__(self):
        return repr(dict([(k, self[k]) for k in self.keys()]))

    def __len__(self):
        return len(self._message.keys())

    def __delitem__(self, key):
        self._del(header=key)

    def keys(self):
        return self._message.keys()

    def values(self):
        return map(lambda k: self[k], self.keys())

    def __cmp__(self, dict):
        raise Exception('Oops')

    def __contains__(self, item):
        return item in self.values()

    def add(self, key, value):
        self.create_header_proxy(key, value)

    def __iter__(self):
        return iter([(k, self[k]) for k in self.keys()])

    def __call__(self):
        raise Exception('Oops')

    def __unicode__(self):
        return unicode(self.__repr__())