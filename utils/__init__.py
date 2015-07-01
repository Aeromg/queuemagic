# -*- coding: utf-8 -*-
__author__ = 'vdv'


def strip_tags(html):
    from html_stripper import HTMLParserStripper

    return HTMLParserStripper.strip_tags(html)


def get_mime_of_file_name(file_name):
    from mime import Mime

    return Mime.get_mime(file_name)


def get_config_reader(config):
    from app.config_provider import ConfigProvider

    return ConfigProvider(config)