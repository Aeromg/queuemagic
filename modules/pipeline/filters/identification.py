# -*- coding: utf-8 -*-
from pipelines.filter import Filter

__author__ = 'vdv'


class Identification(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        self._include_users = self.config.strict('include_users', default=[], types=[str], can_iterate=True)
        self._exclude_users = self.config.strict('exclude_users', default=[], types=[str], can_iterate=True)
        self._include_member_of = self.config.strict('include_member_of', default=[], types=[str], can_iterate=True)
        self._exclude_member_of = self.config.strict('exclude_member_of', default=[], types=[str], can_iterate=True)
        self._sender_location = self.config.strict('sender_location', default='any', types=[str],
                                                   values=['any', 'internal', 'external'])

    def test(self):
        auth = self.bus.identity

        if auth is None:
            return self._sender_location in ['any', 'external']

        sender_location_ok = self._sender_location != 'external'
        include_users_ok = auth.account in self._include_users if len(self._include_users) > 0 else True
        exclude_users_ok = auth.account not in self._exclude_users if len(self._exclude_users) > 0 else True

        exclude_member_of_fail = len(self._exclude_member_of) > 0
        for group in auth.groups:
            if group in self._exclude_member_of:
                exclude_member_of_fail = True
                break

        include_member_of_fail = len(self._include_member_of) > 0
        for group in auth.groups:
            if group in self._include_member_of:
                include_member_of_fail = False
                break

        return include_users_ok and \
               exclude_users_ok and \
               not exclude_member_of_fail and \
               not include_member_of_fail and \
               sender_location_ok
