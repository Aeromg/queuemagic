# -*- coding: utf-8 -*-
from StringIO import StringIO
from messages.mail import EmailFacade

__author__ = 'vdv'


class EmailSnapshot(object):
    def __init__(self, email, previous=None):
        assert isinstance(email, EmailFacade)
        assert previous is None or isinstance(previous, EmailSnapshot)

        self._email = email
        self._previous = previous

    @property
    def version(self):
        return 0 if self.previous is None else self.previous.version + 1

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    @property
    def previous(self):
        return self._previous

    def discard(self):
        self._email = None
        self._previous = None

    def get_root(self):
        step = self
        while step.previous:
            step = step.previous

        return step


class EmailSnapshotBranch(object):
    def __init__(self, email):
        assert isinstance(email, EmailFacade)

        self._current = EmailSnapshot(email=email)

    @property
    def version(self):
        return self._current.version

    @property
    def email(self):
        return self._current.email

    def push(self):
        fd = StringIO()
        self.email.write_to(fd)
        fd.seek(0)
        self._current = EmailSnapshot(email=EmailFacade(fd=fd), previous=self._current)
        fd.close()

    def pull(self):
        prev = self._current.previous
        prev.email = self.email
        self._current = prev

    def throw(self):
        cur = self._current
        self._current = cur.previous
        cur.discard()

    def pull_all(self):
        root = self._current.get_root()
        root.email = self._current.email
        cur = self._current

        while cur != root:
            cur_pre = cur.previous
            cur.discard()
            cur = cur_pre

        self._current = root

    def throw_all(self):
        root = self._current.get_root()
        cur = self._current

        while cur != root:
            cur_pre = cur.previous
            cur.discard()
            cur = cur_pre

        self._current = root