# -*- coding: utf-8 -*-
__author__ = 'vdv'

'''

import tempfile
import os
import string
import random


class TempFile(object):

    def __init__(self, path, repository, do_not_track):
        assert isinstance(repository, TempFileRepository)

        self._repository = repository
        self._path = path
        self._do_not_track = do_not_track
        self._fd = None
        self._disposed = False

    def open_fd(self, mode):
        if self._fd is None:
            self._fd = open(name=self.path, mode=mode)

        return self._fd

    def close_fd(self):
        if not self._fd is None:
            self._fd.close()

    @property
    def path(self):
        return self._path

    def dispose(self):
        if self._do_not_track or self._disposed:
            return

        self._disposed = True

        try:
            if self._path in self._repository.files.keys():
                del self._repository.files[self._path]
        except:
            pass

        try:
            self.close_fd()
        except:
            pass

        try:
            os.remove(self._path)
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.dispose()

    def __del__(self):
        self.dispose()


class TempFileRepository(object):

    @staticmethod
    def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def __init__(self, config):
        assert isinstance(config, dict)

        self._prefix = config['prefix']
        self._suffix = config['suffix'] if config['suffix'] else 'tmp'
        self._directory = config['directory'] if config['directory'] else tempfile.gettempdir()
        self._temp_files = {}
        self._disposed = False

    def get_temp_file(self, do_not_track=False):
        file_name = None

        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

        while file_name is None or os.path.exists(file_name):
            file_name = os.path.join(self._directory, '{0}{1}.{2}'.format(self._prefix,
                                                                          TempFileRepository.generate_id(size=8),
                                                                          self._suffix))

        temp_file = TempFile(file_name, self, do_not_track)
        if not do_not_track:
            self._temp_files[file_name] = temp_file

        return temp_file

    @property
    def files(self):
        return self._temp_files

    def dispose(self):
        if self._disposed:
            return

        self._disposed = True

        for k in self._temp_files.keys():
            try:
                self._temp_files[k].dispose()
            except Exception, e:
                pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.dispose()

    def __del__(self):
        self.dispose()


'''