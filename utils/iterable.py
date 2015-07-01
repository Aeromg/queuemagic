# -*- coding: utf-8 -*-
__author__ = 'vdv'


def first_or_default(iterable, default=None):
    if iterable:
        for element in iterable:
            return element

    return default


def take(iterable, count):
    if count <= 0:
        return

    counted = 0

    for element in iterable:
        yield element
        counted += 1
        if counted >= count:
            return


def skip(iterable, count):
    counted = 0
    while counted < count:
        iterable.next()
        counted += 1

    for element in iterable:
        yield element