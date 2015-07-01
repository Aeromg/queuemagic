# -*- coding: utf-8 -*-
from services.base.logs import Logs

__author__ = 'vdv'

_logger = None


def set_logger(logger):
    assert isinstance(logger, Logs)
    global _logger
    _logger = logger


def log_error(text, error, *args):
    if _logger:
        _logger.error(text, error, *args)


def log_warning(text, error, *args):
    if _logger:
        _logger.warning(text, error, *args)


def log_info(text, *args):
    if _logger:
        _logger.sel(text, *args)


def log_debug(text, *args):
    if _logger:
        _logger.debug(text, *args)