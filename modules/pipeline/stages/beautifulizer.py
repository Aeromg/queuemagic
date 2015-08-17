# -*- coding: utf-8 -*-
import re
from bleach import clean

from pipelines.expression_argument import ExpressionArgument
from pipelines.stage import Stage


__author__ = 'vdv'


class Beautifulizer(Stage):
    REGEX_FLAGS = re.UNICODE + re.MULTILINE + re.IGNORECASE
    LONG_SPACES_REGEX = re.compile('(?<=\s)[ \t]+|(\s+(?=[,.:;]))', REGEX_FLAGS)
    LONG_NEWLINE_REGEX = re.compile('^[ \t]*$', REGEX_FLAGS)
    HYPHEN_REGEX = re.compile('(?<=[ \t])-(?=[ \t])', REGEX_FLAGS)
    COMMA_REGEX = re.compile('\s?,(?<=[\w\W])', REGEX_FLAGS)
    COLON_REGEX = re.compile(' *:(?<=[^/]) *', REGEX_FLAGS)
    DEFAULT_ALLOWED_HTML = ['body', 'html']

    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        self._locations = self.config.strict(key='locations', types=[str], can_iterate=True,
                                             default=['subject', 'body'])
        self._remove_long_spaces = self.config.strict('remove_long_spaces', types=[bool], default=False)
        self._remove_html = self.config.strict('remove_html', types=[bool], default=False)
        self._allowed_html_tags = Beautifulizer.DEFAULT_ALLOWED_HTML + self.config.strict('allowed_html_tags',
                                                                                          types=[str], can_iterate=True,
                                                                                          default=[])
        self._remove_long_newline = self.config.strict('remove_long_newline', types=[bool], default=False)
        self._restore_punctuation = self.config.strict('restore_punctuation', types=[bool], default=False)
        self._sender_name_rewrite = self.config.strict('sender_name_rewrite',
                                                       can_call=True, non_empty=False, default=None)

        self._sender_address_rewrite = self.config.strict('sender_address_rewrite',
                                                          can_call=True, non_empty=False, default=None)

    def get_value_of_location(self, location, html=False):
        if location == 'subject':
            return self.bus.email.subject

        if location == 'body':
            return self.bus.email.html if html else self.bus.email.text

        raise Exception('Unknown location ' + location)

    def set_value_of_location(self, value, location, html=False):
        if location == 'subject':
            self.bus.email.subject = value
            return

        if location == 'body':
            if html:
                self.bus.email.html = value
            else:
                self.bus.email.text = value
            return

        raise Exception('Unknown location ' + location)

    @staticmethod
    def with_html(location):
        return location in ['body']

    def remove_html(self):
        if not self.bus.email.html is None:
            self.bus.email.html = clean(text=self.bus.email.html, tags=self._allowed_html_tags, strip=True)

    def remove_long_newline(self):
        for location in self._locations:
            for html in [True, False] if self.with_html(location) else [False]:
                text = self.get_value_of_location(location=location, html=html)
                if text is None:
                    continue
                text = Beautifulizer.LONG_NEWLINE_REGEX.sub(u'', text)
                self.set_value_of_location(text, location=location, html=html)

    def remove_long_spaces(self):
        for location in self._locations:
            for html in [True, False] if self.with_html(location) else [False]:
                text = self.get_value_of_location(location=location, html=html)
                if text is None:
                    continue
                text = Beautifulizer.LONG_SPACES_REGEX.sub(u'', text)
                self.set_value_of_location(text, location=location, html=html)

    def restore_punctuation(self):
        for location in self._locations:
            for html in [True, False] if self.with_html(location) else [False]:
                text = self.get_value_of_location(location=location, html=html)
                if text is None:
                    continue
                text = Beautifulizer.HYPHEN_REGEX.sub(u' — ', text)
                text = Beautifulizer.COMMA_REGEX.sub(u', ', text)
                text = Beautifulizer.COLON_REGEX.sub(u': ', text)
                self.set_value_of_location(text, location=location, html=html)

    def sender_name_rewrite(self):
        self.bus.email.from_address.name = self._sender_name_rewrite(ExpressionArgument(self.bus))

    def sender_address_rewrite(self):
        self.bus.email.from_address.address = self._sender_address_rewrite(ExpressionArgument(self.bus))

    def execute(self):
        #if self._remove_html:
        #    self.remove_html()

        if self._remove_long_newline:
            self.remove_long_newline()

        if self._remove_long_spaces:
            self.remove_long_spaces()

        if self._restore_punctuation:
            self.restore_punctuation()

        if self._sender_name_rewrite:
            self.sender_name_rewrite()

        if self._sender_address_rewrite:
            self.sender_address_rewrite()

        return True