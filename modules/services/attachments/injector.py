# -*- coding: utf-8 -*-
from messages.mail import EmailFacade
from services.base.attachments import Attachments

__author__ = 'vdv'

import os


class AttachmentInjector(Attachments):
    def __init__(self, config, service_resolver):
        Attachments.__init__(self, config=config, service_resolver=service_resolver)

        self._base_path = self.config.strict(key='path', types=[str], non_empty=True)

    def _get_absolute_path(self, path):
        if os.pathsep in path:
            return path

        return os.path.join(self._base_path, path)

    def inject_path(self, email, path, name=None):
        assert isinstance(email, EmailFacade)
        assert isinstance(path, str) or isinstance(path, unicode)

        if name:
            assert isinstance(name, str) or isinstance(name, unicode)
        else:
            name = os.path.basename(path)

        return email.attachments.add(name=name, path=self._get_absolute_path(path))

    def inject_fd(self, email, fd, name):
        assert isinstance(email, EmailFacade)
        assert isinstance(name, str) or isinstance(name, unicode)

        return email.attachments.add(name=name, fd=fd)