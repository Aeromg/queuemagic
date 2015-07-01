# -*- coding: utf-8 -*-
__author__ = 'vdv'

import re


def get_tags(text):
    return map(lambda s: s.lower()[1:], re.findall('#[\w\W\d_\-]+?\\b', text, flags=re.UNICODE))


def remove_tags(text, tags=None):
    if tags is None or len(tags) == 0:
        return re.sub('(^(#[\w\W\d_\-]+?\\b)\s?)|(\s#[\w\W\d_\-]+?\\b)', '', text, flags=re.UNICODE)

    return re.sub('(^|)?#[\w\W\d_\-]+?\s?\\b', '', text, flags=re.UNICODE)