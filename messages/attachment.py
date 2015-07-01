# -*- coding: utf-8 -*-
from messages.payload_proxy import EmailPayloadProxy

__author__ = 'vdv'

import re
from utils.mime import Mime
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import make_header
from email import Encoders
import time
import os
from app.logger import *


class EmailAttachment(object):
    def __init__(self):
        pass

    @property
    def file_name(self):
        raise Exception('Abstract method call')

    @file_name.setter
    def file_name(self, value):
        raise Exception('Abstract method call')

    def copy_to(self, fd):
        raise Exception('Abstract method call')


class EmailAttachmentInjector(EmailPayloadProxy):
    def __init__(self, payload):
        EmailPayloadProxy.__init__(self, payload)

    def _convert_to_related(self):
        charset = str(self.payload.get_charset())
        sub_type = str(self.payload.get_content_subtype())

        log_debug('Converting to related. Charset {0}, Subtype {1}', charset, sub_type)
        log_debug('mimepart {0}', str(self.payload.get_payload()))
        if not self.payload.is_multipart():
            if charset:
                part = MIMEText(_text=self.payload.get_payload(), _subtype=sub_type, _charset=charset)
            else:
                part = MIMEText(_text=self.payload.get_payload(), _subtype=sub_type)
        else:
            part = MIMEMultipart(_subtype=self.payload.get_content_subtype(),
                                 _subparts=self.payload.get_payload())

        #if 'Content-Transfer-Encoding' in self.payload.keys():
            #part['Content-Transfer-Encoding'] = self.payload['Content-Transfer-Encoding']
            #del self.payload['Content-Transfer-Encoding']

        self.payload.set_type('multipart/related')
        self.payload.set_payload([part])

    def attach_file(self, file_name, display_name=None, content_id=None):
        basename = os.path.basename(file_name) if display_name is None else display_name
        with open(name=file_name, mode='rb') as fd:
            return self.attach_fd(fd=fd, display_name=basename, content_id=content_id)

    def attach_fd(self, fd, display_name, content_id=None):
        u_display_name = display_name
        u_content_id = content_id

        if u_content_id is None:
            u_content_id = '{0}@{1}.{2}'.format(u_display_name, str(time.time()), str(os.getpid()))

        if isinstance(u_display_name, str):
            u_display_name = unicode(u_display_name.decode('utf-8'))

        if isinstance(u_content_id, str):
            u_content_id = unicode(u_content_id.decode('utf-8'))

        encoded_file_name = make_header([(u_display_name, None)]).encode()
        encoded_content_id = make_header([(u_content_id, None)]).encode()

        mime = Mime.get_mime(display_name)

        if self.payload.get_content_type() not in ['multipart/related', 'multipart/muxed']:
            self._convert_to_related()

        part = MIMEBase(mime.split('/')[0], mime.split('/')[1])
        part.set_payload(fd.read())
        part.set_type(part.get_content_type() + '; name=' + encoded_file_name)
        part.add_header('Content-Disposition', 'attachment; filename={0}'.format(encoded_file_name))
        part.add_header('Content-ID', '<{0}>'.format(encoded_content_id))

        Encoders.encode_base64(part)

        self.payload.attach(part)

        return u_content_id


class EmailAttachmentPayloadLinked(EmailAttachment, EmailPayloadProxy):
    def __init__(self, payload):
        EmailPayloadProxy.__init__(self, payload=payload)
        EmailAttachment.__init__(self)

        self._file_name = None

    def _rename_content_type_part(self, value):
        if 'Content-Type' not in self.payload.keys():
            return

        content_type = self.payload['Content-Type']
        content_type = re.sub('(?<=name=).*', value, content_type)
        self.payload.replace_header('Content-Type', content_type)

    def _rename_content_disposition_part(self, value):
        if 'Content-Disposition' not in self.payload.keys():
            return

        content_type = self.payload['Content-Disposition']
        content_type = re.sub('(?<=filename=).*', value, content_type)
        self.payload.replace_header('Content-Disposition', content_type)

    def _rename_content_id_part(self, value):
        if 'Content-ID' not in self.payload.keys():
            return

        content_type = self.payload['Content-ID']
        content_type = re.sub('(?<=<).*(?=>)', value, content_type)
        self.payload.replace_header('Content-ID', content_type)

    @property
    def file_name(self):
        return self.payload.get_filename()

    @file_name.setter
    def file_name(self, value):
        if isinstance(value, str):
            value = unicode(value)

        encoded = make_header([(value, None)]).encode()

        self._rename_content_type_part(encoded)
        self._rename_content_disposition_part(encoded)
        self._rename_content_id_part(encoded)

    def copy_to(self, fd):
        fd.write(self.payload.get_payload(decode=True))


class EmailAttachmentsFacade(EmailPayloadProxy):
    def __init__(self, payload):
        EmailPayloadProxy.__init__(self, payload)

    def add(self, name, fd=None, path=None, cid=None):
        assert (bool(fd) != bool(path)) and (fd is None or path is None)

        if path is None:
            return EmailAttachmentInjector(payload=self.payload).attach_fd(fd=fd, display_name=name,
                                                                           content_id=cid)
        else:
            return EmailAttachmentInjector(payload=self.payload).attach_file(file_name=path, display_name=name,
                                                                             content_id=cid)