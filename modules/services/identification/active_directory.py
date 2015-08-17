# -*- coding: utf-8 -*-
from services.base.cache import Cache

__author__ = 'vdv'

import re
import ldap

from services.base.identification import IdentificationSource
from modules.services.identification.active_directory_record import ActiveDirectoryRecord


class ActiveDirectory(IdentificationSource):
    def __init__(self, config, service_resolver, cache):
        IdentificationSource.__init__(self, config=config, service_resolver=service_resolver)

        assert isinstance(cache, Cache)

        self._dc = self.config.strict('dc', types=[str], non_empty=True)
        self._user = self.config.strict('user', types=[str], non_empty=True)
        self._password = self.config.strict('password', types=[str], non_empty=True)
        self._catalog = self.config.strict('catalog', types=[str], non_empty=True)
        self._wildcard_mail_field = self.config.strict('wildcard_mail_field', types=[str], non_empty=True)
        self._extra_fields = self.config.strict('extra_fields', types=[str], can_iterate=True, non_empty=True)
        self._local_domains = self.config.strict('local_domains', types=[str], can_iterate=True, non_empty=True)
        self._extra_fields_source = self.config.strict('extra_fields_source', types=[str], non_empty=True)

        self._cache = cache
        self._ldap = None

    def _ldap_open(self):
        try:
            self._ldap = ldap.open(self._dc)
            self._ldap.simple_bind(self._user, self._password)
        except ldap.LDAPError:
            self._ldap = None
            raise

    @staticmethod
    def _get_user_query_filter(user):
        return "(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(sAMAccountName=" + user + "))"

    def _get_search_object(self, user):
        if not self._ldap:
            self._ldap_open()

        return self._ldap.search_s(
            self._catalog,
            ldap.SCOPE_SUBTREE,
            ActiveDirectory._get_user_query_filter(user),
            ActiveDirectoryRecord.ldap_object_fields_mapping().keys()+['memberOf', self._extra_fields_source])

    def _add_extra_fields_info_object(self, info_object):
        if 'extra' not in info_object.keys():
            info_object['extra'] = {}

        if self._extra_fields_source in info_object.keys():
            for extra in info_object[self._extra_fields_source].split():
                if not re.match('^.+:.*$', extra):
                    continue

                key = str(re.findall('^.*?(?=:)', extra)[0])
                if key not in self._extra_fields:
                    continue

                value = extra[len(key)+1:]
                info_object['extra'][key] = value

    def _cleanup_info_object(self, info_object):
        for key in info_object:
            if key == self._wildcard_mail_field:
                info_object[key] = 'FIXME'
                #self._strings.get_email_address_for_account(info_object[key])

        info_object['jid'] = 'FIXME'
        #self._strings.get_jid(info_object['sAMAccountName'])

    def _try_get_info_object(self, user):
        search = self._get_search_object(user)

        if len(search) < 1:
            return None

        result = {}
        decode = lambda s: s.decode('unicode_escape').encode('iso8859-1').decode('utf8')
        for item in search[0][1]:
            if len(search[0][1][item]) == 1:
                result[item] = decode(search[0][1][item][0])
            else:
                result[item] = map(decode, search[0][1][item])

        self._add_extra_fields_info_object(result)
        self._cleanup_info_object(result)

        return result

    def _try_cache_get(self, user):
        if self._cache:
            return self._cache.try_get(user)

    def _cache_set(self, info_object, user):
        if self._cache:
            self._cache.set(info_object, user)

    def try_get_auth(self, username):
        """
        :param username: str
        :rtype : services.identification.AuthorityInfo
        """
        assert isinstance(username, str)

        if not ('@' not in username or username.count('@') == 1):
            raise Exception('Invalid user name ' + username)

        if '@' in username:
            user, domain = username.split('@')
        else:
            user = username
            domain = None

        if domain and domain not in self._local_domains:
            return None

        info = self._try_cache_get(user)
        if not info is None:
            return info

        try:
            info_object = self._try_get_info_object(user)
            if info_object is None:
                return None

            info = ActiveDirectoryRecord(info_object)
        except ldap.LDAPError:
            raise

        self._cache_set(info, user)

        return info

    def try_get_account_from_email(self, email):
        assert isinstance(email, str)

        for domain in self._local_domains:
            if email.endswith('@' + domain):
                return re.findall('^.*?(?=@)', email)[0].lower()

        return None