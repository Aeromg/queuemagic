# -*- coding: utf-8 -*-
from services.base.identification import Identification

__author__ = 'vdv'


class ActiveDirectoryRecord(Identification):
    @staticmethod
    def ldap_object_fields_mapping():
        return \
            {
                'department': 'departament',
                'displayName': 'display_name',
                'givenName': 'first_name',
                'mail': 'email',
                'mobile': 'mobile_phone',
                'physicalDeliveryOfficeName': 'office_name',
                'sn': 'last_name',
                'title': 'title',
                'telephoneNumber': 'intercom',
                'company': 'company',
                'homePhone': 'office_phone',
                'streetAddress': 'street_address',
                'l': 'city',
                'co': 'country',
                'postalCode': 'postal_code',
                'proxyAddresses': None,
                'sAMAccountName': 'account',
                'wWWHomePage': 'web'
            }

    def __init__(self, info_object):
        Identification.__init__(self)

        self._info_object = info_object
        for key in ActiveDirectoryRecord.ldap_object_fields_mapping().keys():
            if key not in self._info_object.keys():
                self._info_object[key] = ''

    @property
    def account(self):
        return self._info_object['sAMAccountName']

    @property
    def departament(self):
        return self._info_object['department']

    @property
    def display_name(self):
        return self._info_object['displayName']

    @property
    def first_name(self):
        return self._info_object['givenName']

    @property
    def email(self):
        return self._info_object['mail']

    @property
    def mobile_phone(self):
        return self._info_object['mobile']

    @property
    def office_name(self):
        return self._info_object['physicalDeliveryOfficeName']

    @property
    def last_name(self):
        return self._info_object['sn']

    @property
    def title(self):
        return self._info_object['title']

    @property
    def intercom(self):
        return self._info_object['telephoneNumber']

    @property
    def company(self):
        return self._info_object['company']

    @property
    def office_phone(self):
        return self._info_object['homePhone']

    @property
    def street_address(self):
        return self._info_object['streetAddress']

    @property
    def city(self):
        return self._info_object['l']

    @property
    def country(self):
        return self._info_object['co']

    @property
    def postal_code(self):
        return self._info_object['postalCode']

    @property
    def jid(self):
        return self._info_object['jid']

    @property
    def extra(self):
        return self._info_object['extra']

    @property
    def web(self):
        return self._info_object['wWWHomePage']

    @property
    def groups(self):
        return self._info_object['memberOf']