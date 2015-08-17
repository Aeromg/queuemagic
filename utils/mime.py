# -*- coding: utf-8 -*-
__author__ = 'vdv'

from mimetypes import MimeTypes
from urllib import pathname2url
import os


class Mime(object):
    _mime = MimeTypes()

    def __init__(self):
        raise Exception('Static class constructor')

    @staticmethod
    def get_mime(file_name):
        if '/' in file_name:
            file_name = os.path.basename(file_name)

        t, v = Mime._mime.guess_type(pathname2url(file_name))
        return t