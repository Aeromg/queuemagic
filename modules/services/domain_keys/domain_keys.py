# -*- coding: utf-8 -*-
from messages.mail import EmailFacade
from services.base.domain_keys import DomainKeysSigner as DomainKeysSignerBase
import os
import dkim
from StringIO import StringIO

__author__ = 'vdv'


class DomainKeysSignerDomainConfig(object):
    def __init__(self, domain, private_key, headers, selector):
        self._domain = domain
        self._private_key = private_key
        self._headers = headers
        self._selector = selector

    @property
    def domain(self):
        return self._domain

    @property
    def private_key(self):
        return self._private_key

    @property
    def headers(self):
        return self._headers

    @property
    def selector(self):
        return self._selector


class DomainKeysSigner(DomainKeysSignerBase):
    def __init__(self, config, service_resolver):
        DomainKeysSignerBase.__init__(self, config=config, service_resolver=service_resolver)

        self._domains = {}
        for domain in self.config.strict('domains', can_iterate=True, default=[]):
            self._domains[domain['name']] = domain

        self._local_domains = self._domains.keys()

        self._headers = self.config.strict('headers', types=[str], can_iterate=True, non_empty=True)
        self._selector = self.config.strict('selector', types=[str], default='mail')

        self._default_domain_enabled = self.config.strict('default_domain.enabled', types=[bool], default=False)
        self._default_domain_pattern = self.config.strict('default_domain.private_key', types=[str], non_empty=False)
        self._default_dkim_selector = self.config.strict('default_domain.selector', types=[str], default=self._selector)

    def _try_get_domain_config(self, domain):
        if domain in self._local_domains:
            conf = self._domains[domain]
            return DomainKeysSignerDomainConfig(domain=domain,
                                                private_key=conf['private_key'],
                                                headers=conf['headers'] if 'headers' in conf.keys() else self._headers,
                                                selector=conf['selector'] if 'selector' in conf.keys() else self._selector)

        domain_parts = domain.split('.')
        for i in xrange(0, len(domain_parts)):
            tld = '.'.join(domain_parts[i:])
            if tld in self._local_domains:
                conf = self._domains[tld]
                if 'with_subdomains' in conf.keys() and conf['with_subdomains']:
                    return DomainKeysSignerDomainConfig(domain=domain,
                                                        private_key=conf['private_key'],
                                                        headers=conf['headers'] if 'headers' in conf.keys() else self._headers,
                                                        selector=conf['selector'] if 'selector' in conf.keys() else self._selector)

        if not self._default_domain_enabled:
            return None

        return DomainKeysSignerDomainConfig(domain=domain,
                                            private_key=self._default_domain_pattern.replace('{domain}', domain),
                                            headers=self._headers,
                                            selector=self._default_dkim_selector)

    def get_sign(self, email, sender=None):
        assert isinstance(email, EmailFacade)
        sender_address = email.from_address.address if sender is None else sender
        #todo: validation!

        if sender_address.count('@') != 1:
            raise Exception('Invalid from address format')

        user, domain = sender_address.split('@')

        domain_config = self._try_get_domain_config(domain)

        if domain_config is None:
            raise Exception('Unknown sender domain ' + domain)

        if not os.path.exists(domain_config.private_key):
            raise Exception('No private key file ' + domain_config.private_key)

        with open(name=domain_config.private_key, mode='r') as fd:
            key_data = fd.read()

        fd = StringIO()
        email.write_to(fd)
        fd.seek(0)

        signature = dkim.sign(message=fd.read(),
                              selector=domain_config.selector,
                              domain=domain_config.domain,
                              include_headers=domain_config.headers,
                              privkey=key_data)

        fd.close()

        return signature.replace('DKIM-Signature: ', '')