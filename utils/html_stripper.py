# -*- coding: utf-8 -*-
__author__ = 'vdv'

from HTMLParser import HTMLParser
import re


class HTMLParserStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

    @staticmethod
    def strip_tags(html):
        s = HTMLParserStripper()
        s.feed(html)

        text = s.get_data()
        if '\r\n' in text:
            lines = text.split('\r\n')
        else:
            lines = text.split('\n')

        lines = map(lambda l: re.sub('\s+', ' ', l), lines)
        lines = map(lambda l: re.sub('\s{2,}', '', l), lines)
        lines = map(lambda l: re.sub('^\s+|\s+$', '', l), lines)
        lines = [l for l in lines if len(re.sub('\s', '', l)) > 0]

        return '\r\n'.join(lines)