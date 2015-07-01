# -*- coding: utf-8 -*-
from pipelines.stage import Stage
from utils.hashtag import remove_tags

__author__ = 'vdv'


class RemoveHashTag(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        self._locations = self.config.strict(key='locations', types=[str], can_iterate=True,
                                             default=['subject'], values=['subject', 'body'])
        self._tags = self.config.strict(key='tags', types=[unicode, str], can_iterate=True, default=[])

    def _remove_hash_tag(self, text):
        return remove_tags(text=text, tags=self._tags)

    def execute(self):
        locations = self._locations
        email = self.bus.email
        tags = self._tags

        if 'subject' in locations:
            email.subject = remove_tags(text=email.subject, tags=tags)

        if 'body' in locations:
            if email.text:
                email.text = remove_tags(text=email.text, tags=tags)

            if email.html:
                email.html = remove_tags(text=email.html, tags=tags)

        return True