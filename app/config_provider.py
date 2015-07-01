# -*- coding: utf-8 -*-
import collections
import re

__author__ = 'vdv'


class ConfigProvider(object):
    def __init__(self):
        pass

    def get(self, key):
        """
        :param key: str
        :raise Exception: KeyError
        """
        raise Exception('Method must be overridden')

    def try_get(self, key, default=None):
        raise Exception('Method must be overridden')

    def strict(self, key, default=None, types=None, values=None, can_call=None, can_iterate=None, non_empty=False):
        raise Exception('Method must be overridden')

    def section(self, key):
        """
        :param key: str
        :rtype : ConfigProvider
        """
        raise Exception('Method must be overridden')

    def keys(self, path=None):
        """
        :rtype : list
        """
        raise Exception('Method must be overridden')

    @property
    def base_key(self):
        """
        :rtype : str
        """
        raise Exception('Method must be overridden')


class ConfigSectionRoot(ConfigProvider):
    def __init__(self, dictionary=None):
        ConfigProvider.__init__(self)
        assert dictionary is None or isinstance(dictionary, dict) or isinstance(dictionary, list)

        self._data = []

        if isinstance(dictionary, list):
            assert all(map(lambda d: isinstance(d, dict), dictionary))
            for config in dictionary:
                self.append(config)
        else:
            self.append(dictionary)

    def _get_navigated(self, dictionary, path):
        current_node = dictionary

        if path in current_node.keys():
            return current_node[path]

        for node_key in path.split('.'):
            if isinstance(current_node, str):
                current_node = self._unpack_value(current_node)

            if node_key in current_node.keys():
                current_node = current_node[node_key]
            else:
                raise KeyError('No key path [' + path + ']')

        if isinstance(current_node, str):
            current_node = self._unpack_value(current_node)

        return current_node

    def _unpack_value(self, value):
        if isinstance(value, str):
            tokens = re.findall('{{.*?}}', value)
            if len(tokens) > 0:
                if re.match('^{{.*?}}$', value) and len(tokens) == 1:
                    value = self.get(tokens[0].strip('{}'))
                else:
                    for token in tokens:
                        value = value.replace(token, self.get(token.strip('{}')))

        return value

    def get(self, key):
        value_taken = False
        value = None

        for i in xrange(0, len(self._data)):
            try:
                value = self._get_navigated(dictionary=self._data[i], path=key)
                value_taken = True
                break
            except KeyError:
                pass

        if not value_taken:
            raise KeyError('No key path [' + key + ']')

        return self._unpack_value(value)

    def try_get(self, key, default=None):
        try:
            return self.get(key)
        except KeyError:
            return default

    def strict(self, key, default=None, types=None, values=None, can_call=None, can_iterate=None, non_empty=False):
        value = self.try_get(key=key, default=default)

        if non_empty:
            assert value

        if can_call and not (default is None):
            assert callable(value)

        types_list = None
        if types:
            types_list = list(types)

            if type(default) not in types_list:
                types_list.append(type(default))

        if can_iterate:
            assert isinstance(value, collections.Iterable)

        values_list = None
        if values:
            values_list = list(values)

            if default not in values_list:
                values_list.append(default)

        if can_iterate:
            for v in value:
                if types_list:
                    assert any(map(lambda t: isinstance(v, t), types_list))
                if values_list:
                    assert v in values_list
        else:
            if types_list:
                assert any(map(lambda t: isinstance(value, t), types_list))
            if values_list:
                assert value in values_list

        return value

    def section(self, key):
        assert key
        assert isinstance(self.get(key), dict)

        return ConfigSection(provider=self, base=key)

    def keys(self, path=None):
        if path is None:
            return list(set([keys for dictionary in self._data for keys in dictionary.keys()]))

        keys_taken = False
        keys_set = set()
        for i in xrange(0, len(self._data)):
            try:
                for key in self._get_navigated(dictionary=self._data[i], path=path).keys():
                    keys_set.add(key)
                keys_taken = True
            except KeyError:
                pass

        if not keys_taken:
            raise KeyError('No key path [' + path + ']')

        return list(keys_set)

    def add(self, dictionary, priority=0):
        assert isinstance(dictionary, dict)

        self._data.insert(priority, dictionary)

    def append(self, dictionary):
        self._data.append(dictionary)

    @property
    def base_key(self):
        """
        :rtype : str
        """
        return ''


class ConfigSection(ConfigProvider):
    def __init__(self, provider, base):
        ConfigProvider.__init__(self)

        assert isinstance(provider, ConfigProvider)
        assert isinstance(base, str)

        self._provider = provider
        self._base = base

    def _get_absolute_key(self, relative_key):
        if relative_key is None:
            return self._base

        return '{0}.{1}'.format(self._base, relative_key)

    def get(self, key):
        return self._provider.get(key=self._get_absolute_key(relative_key=key))

    def try_get(self, key, default=None):
        return self._provider.try_get(key=self._get_absolute_key(relative_key=key),
                                      default=default)

    def strict(self, key, default=None, types=None, values=None, can_call=None, can_iterate=None, non_empty=False):
        return self._provider.strict(key=self._get_absolute_key(relative_key=key), default=default,
                                     types=types, values=values, can_call=can_call,
                                     can_iterate=can_iterate, non_empty=non_empty)

    def section(self, key):
        return self._provider.section(key=self._get_absolute_key(relative_key=key))

    def keys(self, path=None):
        absolute_path = self._get_absolute_key(relative_key=path)
        return self._provider.keys(path=absolute_path)

    @property
    def base_key(self):
        """
        :rtype : str
        """
        return self._base