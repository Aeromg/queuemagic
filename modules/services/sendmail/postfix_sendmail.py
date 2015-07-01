# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
from StringIO import StringIO
from messages.mail import EmailFacade
from services.base.sendmail import SendMail
from app.logger import *

__author__ = 'vdv'


class PostfixSendMail(SendMail):
    def __init__(self, config, service_resolver):
        SendMail.__init__(self, config=config, service_resolver=service_resolver)

        self._bin = self.config.strict('bin', types=[str], non_empty=True)
        self._args = self.config.strict('args', types=[str], can_iterate=True, non_empty=False, default=[])

    def send(self, email, recipients=None, sender=None):
        assert isinstance(email, EmailFacade)

        if recipients is None:
            recipients = map(lambda x: x.address, email.to_addresses)

        if sender is None:
            sender = email.from_address.address

        log_debug('Send email from {0} to {1}', str(sender), ', '.join(recipients))
        args = [self._bin] + self._args + [sender] + ['--'] + list(recipients)

        log_debug('Subprocess {0}', ' '.join(args))

        p = Popen(args=args, stdout=PIPE, stdin=PIPE)
        fd = StringIO()
        email.write_to(fd=fd)
        fd.seek(0)
        p.communicate(input=fd.read())

        return p.wait()