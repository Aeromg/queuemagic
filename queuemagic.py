#! /usr/bin/python
# -*- coding: utf-8 -*-
import traceback
from StringIO import StringIO
from app.config_provider import ConfigProvider, ConfigSectionRoot
from app.logger import *
from messages.mail import EmailFacade
from pipelines.pipeline import FailAction
from services.base.logs import Logs
from services.base.pipeline import PipelineService
from services.base.sendmail import SendMail
from services.base.statistics import Statistics
from services.resolver import ServiceResolver
from userconfig import config

__author__ = 'vdv'

import argparse
import sys
from subprocess import Popen, PIPE
import shlex
import shutil
import os


class QueueMagicCliArguments(object):
    @staticmethod
    def _make_parser():
        parser = argparse.ArgumentParser(
            description='QM',
            version='VERS',
        )
        parser.add_argument('-c', '--config', type=str, nargs='+', required=False,
                            help='configuration file')

        parser.add_argument('-p', '--pipeline', type=str, required=True,
                            help='pipeline name')

        parser.add_argument('-i', '--input', type=str, nargs='+', required=False,
                            help='input rfc822 file')

        parser.add_argument('-o', '--output', type=str, nargs='+', required=False,
                            help='output rfc822 file')

        parser.add_argument('-m', '--mute', action='store_true', required=False,
                            help='do not write any to stdout')

        parser.add_argument('-s', '--sender', type=str, required=False,
                            help='sender email address')

        parser.add_argument('-u', '--sasl-username', type=str, required=False,
                            help='sender sasl username')

        parser.add_argument('-a', '--sender-ip', type=str, required=False,
                            help='sender ip address')

        parser.add_argument('-r', '--recipient', type=str, required=False,
                            help='recipient email address')

        parser.add_argument('-d', '--delete-input', type=bool, default=False, required=False,
                            help='delete input file after all')

        parser.add_argument('-e', '--extra', type=str, nargs='+', required=False,
                            help='pass extra arguments to pipeline')

        parser.add_argument('-x', '--output-exec', type=str, nargs='+', required=False,
                            help='pass output to external command')

        parser.add_argument('-n', '--no-stat', type=bool, default=False, required=False,
                            help='do not collect statistics')

        parser.add_argument('--verbose', action='store_true', required=False,
                            help='pass output to external command')

        parser.add_argument('--send', action='store_true', required=False,
                            help='attempt to send')

        return parser

    def __init__(self):
        self._parser = QueueMagicCliArguments._make_parser()
        self._args = self._parser.parse_args()
        self._test()

    def _test(self):
        assert not (not self.input and self.delete_input)
        if self.output_exec:
            assert not self.output

    @property
    def config(self):
        return ' '.join(self._args.config) if self._args.config else None

    @property
    def pipeline(self):
        return self._args.pipeline

    @property
    def input(self):
        return ' '.join(self._args.input) if self._args.input else None

    @property
    def output(self):
        return ' '.join(self._args.output) if self._args.output else None

    @property
    def sender(self):
        return self._args.sender

    @property
    def recipient(self):
        return self._args.recipient

    @property
    def delete_input(self):
        return self._args.delete_input

    @property
    def should_use_stdin(self):
        return self.input is None

    @property
    def should_use_stout(self):
        return self.output is None and not self.should_output_exec and not self._args.mute

    @property
    def output_exec(self):
        return ' '.join(self._args.output_exec) if self._args.output_exec else None

    @property
    def should_output_exec(self):
        return not self.output_exec is None

    @property
    def verbose(self):
        return self._args.verbose

    @property
    def should_feed_statistics(self):
        return not self._args.no_stat

    @property
    def should_send(self):
        return self._args.send

    @property
    def sender_ip(self):
        return self._args.sender_ip

    @property
    def data(self):
        data = {}

        if self.sender:
            data['sender'] = self.sender

        if self.recipient:
            data['recipient'] = self.recipient

        if self.sasl_username:
            data['sasl_username'] = self.sasl_username

        if self.sender_ip:
            data['sender_ip'] = self.sender_ip

        return data

    @property
    def sasl_username(self):
        return self._args.sasl_username


class QueueMagicCli(object):
    def __init__(self, config, cli_args):
        assert isinstance(config, ConfigProvider)
        assert isinstance(cli_args, QueueMagicCliArguments)

        self._config = config
        self._args = cli_args
        self._app = ServiceResolver(config=config.section('services'))

        set_logger(self._app.get_service(Logs))

    def _get_email(self):
        if self._args.should_use_stdin:
            log_debug('read stdin smtp message')
            return EmailFacade(fd=sys.stdin)
        else:
            log_debug('read "{0}" smtp message', self._args.input)
            return EmailFacade(file_path=self._args.input)

    def _print_email(self, email):
        log_debug('write output smtp message to stdout')
        email.write_to(sys.stdout)

    def _output_exec(self, email):
        log_debug('attempt to start subprocess "{0}"', self._args.output_exec)
        fd = StringIO()
        email.write_to(fd)
        fd.seek(0)
        p = Popen(args=shlex.split(self._args.output_exec), stdout=PIPE,stdin=PIPE)
        p.communicate(input=fd.read())
        p.wait()

        if p.returncode != 0:
            log_warning('subprocess "{0}" exits with code "{1}"', None, self._args.output_exec, p.returncode)
        else:
            log_debug('subprocess terminated with no errors')

        return p.returncode

    def _get_pipeline(self, email):
        log_debug('building pipeline "{0}"', self._args.pipeline)
        svc = self._app.get_service(PipelineService)
        pipeline = svc.build_pipeline(name=self._args.pipeline, message=email, data=self._args.data)
        log_debug('pipeline building complete')

        return pipeline

    def _feed_statistics(self, pipeline):
        log_debug('feeding statistics')
        svc = self._app.get_service(Statistics)
        assert isinstance(svc, Statistics)

        svc.increment_message_number(sender=pipeline.bus.sender, recipient=pipeline.bus.recipient)
        svc.update_last_message_timestamp(sender=pipeline.bus.sender, recipient=pipeline.bus.recipient)
        log_debug('feeding statistics complete')

    def _send(self, email, sender, recipient):
        svc = self._app.get_service(SendMail)
        assert isinstance(svc, SendMail)

        return svc.send(email=email, sender=sender, recipients=[recipient])

    def run(self):
        return_code = 0
        pipeline_exec_result = False
        pipeline = None

        try:
            email = self._get_email()
        except Exception, e:
            log_error('Unable to fetch email', error=e)
            sys.exit(74)

        try:
            pipeline = self._get_pipeline(email=email)
            if pipeline is None:
                raise Exception('Unable to create pipeline ' + self._args.pipeline)
        except Exception, e:
            log_error('Unable to create pipeline ' + self._args.pipeline, error=e)
            sys.exit(74)

        try:
            pipeline_exec_result = pipeline.execute()
        except Exception, e:
            log_error('Pipeline execution error', e)
            sys.exit(74)

        if not pipeline_exec_result and pipeline.on_fail == FailAction.Drop:
            print('Broken pipeline policies has rejected this message')
            sys.exit(74)

        if self._args.should_feed_statistics:
            try:
                self._feed_statistics(pipeline=pipeline)
            except Exception, e:
                log_error('Unable to feed statistics', e)

        email = pipeline.bus.email

        if self._args.should_use_stout:
            self._print_email(email=email)
        elif self._args.should_output_exec:
            try:
                return_code = self._output_exec(email=email)
            except Exception, e:
                log_error('Subprocess execution failed', e)
                return_code = 74

        if self._args.should_send:
            try:
                return_code = self._send(email=email, sender=self._args.sender, recipient=self._args.recipient)
            except Exception, e:
                log_error('SendMail service execution failed', e)
                return_code = 74

        if self._args.verbose:
            print(pipeline.bus.data)

        if self._args.delete_input:
            try:
                os.remove(self._args.input)
            except Exception, e:
                log_error('Unable to delete input file', e)

        log_debug('execution completed with {0}', str(pipeline.bus.data))

        return return_code

cfg = ConfigSectionRoot(dictionary=config)
args = QueueMagicCliArguments()
cli = QueueMagicCli(config=cfg, cli_args=args)
sys.exit(cli.run())