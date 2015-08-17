# -*- coding: utf-8 -*-
from messages.attachment import EmailAttachmentsFacade
from messages.payload_proxy import EmailPayloadProxy

__author__ = 'vdv'

from email.message import Message
from email import message_from_file, Utils
from email import message_from_string
from messages.headers_aggregator import EmailHeadersAggregator
from messages.text_aggregator import EmailTextContentAggregator

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def _message_from_fd(fd):
    return message_from_file(fd)


def _message_from_path(file_path):
    with open(name=file_path, mode='r') as fd:
        return _message_from_fd(fd)


def _message_from_string(text):
    return message_from_string(text)


class EmailFacade(object):
    def __init__(self, fd=None, file_path=None, text=None, message=None):
        assert len([arg for arg in [fd, file_path, text, message] if bool(arg)]) == 1

        payload = \
            _message_from_fd(fd) if fd else \
                _message_from_path(file_path) if file_path else \
                    _message_from_string(text) if text else \
                        message

        assert isinstance(payload, Message)

        self._payload = payload
        self._header = None

    def get_payload_proxy(self):
        # убрать нахер позже
        return EmailPayloadProxy(self._payload)

    @property
    def size(self):
        return len(self._payload.as_string())

    @property
    def header(self):
        if self._header is None:
            self._header = EmailHeadersAggregator(message=self._payload)

        return self._header

    @property
    def text_content(self):
        return EmailTextContentAggregator(payload=self._payload)

    @property
    def from_address(self):
        return self.header['From']

    @property
    def to_addresses(self):
        return self.header['To']

    @property
    def carbon_copy(self):
        return self.header['cc']

    @property
    def blind_carbon_copy(self):
        return self.header['bcc']

    @property
    def subject(self):
        return self.header['Subject']

    @subject.setter
    def subject(self, value):
        self.header['Subject'] = value

    @property
    def is_dkim_signed(self):
        return self.header.contains('DKIM-Signature')

    @property
    def is_reply(self):
        return self.header.contains('In-Reply-To')

    @property
    def is_forward(self):
        return self.is_reply and self.header['Subject'].lower().startswith('fwd:')

    @property
    def is_referenced(self):
        return self.header.contains('References') or self.is_reply

    @property
    def html(self):
        proxy = self.text_content.get_html_body()
        if proxy is None:
            return None

        return proxy.get_text()

    @html.setter
    def html(self, value):
        proxy = self.text_content.get_html_body()
        if proxy is None:
            return

        proxy.set_text(value)

    @property
    def text(self):
        proxy = self.text_content.get_plain_text_body()
        if proxy is None:
            return None

        return proxy.get_text()

    @text.setter
    def text(self, value):
        proxy = self.text_content.get_plain_text_body()
        if proxy is None:
            return

        proxy.set_text(value)

    @property
    def attachments(self):
        return EmailAttachmentsFacade(self._payload)

    def write_to(self, fd):
        fd.write(self._payload.as_string())

    @staticmethod
    def generate(alternative=False, subject=None, plain=None, html=None, sender_address=None, sender_name=None):
        alternative = alternative or not html is None
        if alternative:
            message = MIMEMultipart('alternative')
            message.attach(MIMEText('', 'plain'))
            message.attach(MIMEText('', 'html'))
        else:
            message = MIMEText('', 'plain')

        message['Date'] = Utils.formatdate(localtime=1)
        message['Message-ID'] = Utils.make_msgid()

        facade = EmailFacade(message=message)

        if subject:
            facade.subject = subject

        if plain:
            facade.text = plain

        if html:
            facade.html = html

        if sender_address:
            facade.from_address.address = sender_address
            if sender_name:
                facade.from_address.name = sender_name

        return facade