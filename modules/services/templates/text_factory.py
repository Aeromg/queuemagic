# -*- coding: utf-8 -*-
import os
import codecs

__author__ = 'vdv'

from services.base.text_factory import TextFactory as TextFactoryBase


class TextFactory(TextFactoryBase):
    def __init__(self, config, service_resolver, environment):
        TextFactoryBase.__init__(self, config=config, service_resolver=service_resolver)

        self._common_view_bag = self.config.strict('view_bag', types=[dict], default={}).copy()
        self._env = environment

    def _get_file_path(self, template):
        file_name = self.config.section('map').strict(key=template, types=[str], non_empty=True)
        if os.pathsep in file_name:
            return file_name
        else:
            template_store = self.config.strict(key='store', types=[str], non_empty=True)
            return os.path.join(template_store, file_name)

    def get_text(self, view_bag, template):
        view_bag_copy = self._common_view_bag
        view_bag_copy.update(view_bag)

        with codecs.open(self._get_file_path(template), mode='r', encoding='utf-8') as fd:
            return self._env.from_string(fd.read()).render(view_bag_copy)