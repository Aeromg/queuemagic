# -*- coding: utf-8 -*-
__author__ = 'vdv'


class NotifyChanged(object):
    def __init__(self):
        self._changed_event_handlers = []

    @property
    def changed(self):
        return self._changed_event_handlers

    def on_changed(self):
        for handler in self.changed:
            if not handler is None:
                handler(self)