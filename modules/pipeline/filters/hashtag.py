# -*- coding: utf-8 -*-
from pipelines.filter import Filter
from utils.hashtag import get_tags

__author__ = 'vdv'


class HashTag(Filter):
    def __init__(self, name, bus, config, service_resolver):
        Filter.__init__(self, name=name, config=config, bus=bus, service_resolver=service_resolver)

        self._tags = self.config.strict(key='tags', types=[unicode, str], can_iterate=True, default=[])
        self._take = self.config.strict(key='take', types=[str], values=['all', 'any', 'one'], default='any')
        self._locations = self.config.strict(key='locations', types=[str], can_iterate=True, default=['subject'])

    def test(self):
        if self._take == 'all' and len(self._tags) == 0:
            return False

        email = self.bus.email

        message_tags = set()
        for location in self._locations:
            if location == 'subject':
                message_tags.update(get_tags(email.subject))

            if location == 'body':
                if email.text:
                    message_tags.update(get_tags(email.text))

                if email.html:
                    message_tags.update(get_tags(email.html))

        if self._take == 'any':
            if len(message_tags) > 0 and len(self._tags) == 0:
                return True

        if self._take == 'all':
            return message_tags.issuperset(set(self._tags))

        if self._take == 'any':
            for tag in message_tags:
                if tag in self._tags:
                    return True

            return False

        if self._take == 'one':
            taken = False
            for tag in message_tags:
                if tag in self._tags:
                    if not taken:
                        taken = True
                    else:
                        return False
            return True

        return False