# -*- coding: utf-8 -*-
from pipelines.stage import Stage
from services.base.attachments import Attachments

__author__ = 'vdv'


class LogoInject(Stage):
    def __init__(self, name, config, bus, filter, service_resolver):
        Stage.__init__(self, name=name, config=config, bus=bus, filter=filter, service_resolver=service_resolver)

        self._is_optional = self.config.strict('optional', default=False, types=[bool])
        self._default_logo = self.config.strict('default', default=None, types=[str])
        self._user_def = self.config.strict('user_def', default=None, types=[str])
        self._display = self.config.strict('display', default=None, types=[str])
        self._id = self.config.strict('id', types=[str], non_empty=True)

        svc = self.service_resolver.get_service(Attachments)
        assert isinstance(svc, Attachments)
        self._service = svc

    def execute(self):
        if self._default_logo is None and self._user_def is None and not self._is_optional:
            raise Exception('No images defined and [optional] isn\'t set')

        optional = self._is_optional

        auth = self.bus.identity
        if not auth is None and self._user_def in auth.extra.keys():
            image = auth.extra[self._user_def]
        else:
            image = self._default_logo

        if not image:
            if not optional:
                raise Exception('No image')
            else:
                return True

        image_id = self._id
        display = self._display

        try:
            cid = self._service.inject_path(email=self.bus.email,
                                            path=image,
                                            name=display)
            self.bus.append_module_data(module=self, key='images', data={image_id: cid})
        except:
            if not optional:
                raise

        return True