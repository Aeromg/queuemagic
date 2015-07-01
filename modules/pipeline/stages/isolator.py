# -*- coding: utf-8 -*-
from messages.address import EmailAddress
from pipelines.stage import Stage
from utils.iterable import first_or_default
__author__ = 'vdv'


class Isolator(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)
        self._headers = self.config.strict(key='headers', types=[str], can_iterate=True, default=['To', 'Cc', 'Bcc'])
        self._undisclosed = self.config.strict(key='undisclosed', types=[bool], default=False)

        assert set(self._headers).issubset({'To', 'Cc', 'Bcc'})

    def execute(self):
        email = self.bus.email

        recipient = None

        headers = [h for h in self._headers if h in email.header.keys()]

        for header in headers:
            proxy = email.header[header]
            recipient = first_or_default([r for r in proxy if r.address == self.bus.recipient])
            if not recipient is None:
                break

        if recipient is None:
            #raise Exception('No <{0}> address in To: header'.format(self.bus.recipient))
            recipient = EmailAddress(address=self.bus.recipient)

        for header in headers:
            proxy = email.header[header]
            del proxy[:]

        if self._undisclosed:
            email.to_addresses.append(EmailAddress(decoded_name='undisclosed-recipients:;', address=''))
            email.blind_carbon_copy.append(recipient)
        else:
            email.to_addresses.append(recipient)

        return True

    @property
    def can_fork(self):
        return True