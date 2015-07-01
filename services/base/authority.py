# -*- coding: utf-8 -*-
from services.service import Service

__author__ = 'vdv'


class AuthoritySource(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def try_get_auth(self, username):
        """
        :rtype : AuthorityInfo
        """
        raise Exception('Abstract method call')


class AuthorityInfo(object):
    def __init__(self):
        raise Exception('Abstract class init')

    @property
    def account(self):
        raise Exception("Abstract method call")

    @property
    def departament(self):
        raise Exception("Abstract method call")

    @property
    def display_name(self):
        raise Exception("Abstract method call")

    @property
    def first_name(self):
        raise Exception("Abstract method call")

    @property
    def email(self):
        raise Exception("Abstract method call")

    @property
    def mobile_phone(self):
        raise Exception("Abstract method call")

    @property
    def office_name(self):
        raise Exception("Abstract method call")

    @property
    def last_name(self):
        raise Exception("Abstract method call")

    @property
    def title(self):
        raise Exception("Abstract method call")

    @property
    def intercom(self):
        raise Exception("Abstract method call")

    @property
    def company(self):
        raise Exception("Abstract method call")

    @property
    def office_phone(self):
        raise Exception("Abstract method call")

    @property
    def street_address(self):
        raise Exception("Abstract method call")

    @property
    def city(self):
        raise Exception("Abstract method call")

    @property
    def country(self):
        raise Exception("Abstract method call")

    @property
    def postal_code(self):
        raise Exception("Abstract method call")

    @property
    def jid(self):
        raise Exception("Abstract method call")

    @property
    def extra(self):
        raise Exception("Abstract method call")

    @property
    def web(self):
        raise Exception("Abstract method call")

    @property
    def groups(self):
        raise Exception("Abstract method call")