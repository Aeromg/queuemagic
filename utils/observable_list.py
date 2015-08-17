# -*- coding: utf-8 -*-
__author__ = 'vdv'

from utils.notify_changed import NotifyChanged

# noinspection PyUnusedLocal
class ObservableList(list, NotifyChanged):
    class NullObserver(object):
        """
        If a call to a method is made, this class prints the name of the method
        and all arguments.
        """

        def __init__(self, observable):
            self._observable = observable

        def p(self, *args):
            self._observable.on_changed()

        def __getattr__(self, attr):
            self.attr = attr
            return self.p

    def __init__(self, value, observer=None):
        list.__init__(self, value)
        NotifyChanged.__init__(self)

        self.set_observer(observer if observer else ObservableList.NullObserver(self))

    def set_observer(self, observer):
        """
        All changes to this list will trigger calls to observer methods.
        """
        self.observer = observer

    def __setitem__(self, key, value):
        """
        Intercept the l[key]=value operations.
        Also covers slice assignment.
        """
        try:
            oldvalue = self.__getitem__(key)
        except KeyError:
            list.__setitem__(self, key, value)
            self.observer.list_create(self, key)
        else:
            list.__setitem__(self, key, value)
            self.observer.list_set(self, key, oldvalue)

    def __delitem__(self, key):
        oldvalue = list.__getitem__(self, key)
        list.__delitem__(self, key)
        self.observer.list_del(self, key, oldvalue)

    def __setslice__(self, i, j, sequence):
        oldvalue = list.__getslice__(self, i, j)
        self.observer.list_setslice(self, i, j, sequence, oldvalue)
        list.__setslice__(self, i, j, sequence)

    def __delslice__(self, i, j):
        oldvalue = list.__getitem__(self, slice(i, j))
        list.__delslice__(self, i, j)
        self.observer.list_delslice(self, i, oldvalue)

    def append(self, value):
        list.append(self, value)
        self.observer.list_append(self)

    def pop(self):
        oldvalue = list.pop(self)
        self.observer.list_pop(self, oldvalue)

    def extend(self, newvalue):
        list.extend(self, newvalue)
        self.observer.list_extend(self, newvalue)

    def insert(self, i, element):
        list.insert(self, i, element)
        self.observer.list_insert(self, i, element)

    def remove(self, element):
        index = list.index(self, element)
        list.remove(self, element)
        self.observer.list_remove(self, index, element)

    def reverse(self):
        list.reverse(self)
        self.observer.list_reverse(self)

    def sort(self, cmpfunc=None):
        oldlist = self[:]
        list.sort(self, cmpfunc)
        self.observer.list_sort(self, oldlist)