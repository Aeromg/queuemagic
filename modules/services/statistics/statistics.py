# -*- coding: utf-8 -*-
__author__ = 'vdv'

import time

from services.base.db import PersistentDictionary
from services.base.statistics import Statistics as StatisticsBase


class Statistics(StatisticsBase):
    def __init__(self, config, service_resolver):
        StatisticsBase.__init__(self, config=config, service_resolver=service_resolver)

        self._db_config = self.config.section('db') if 'db' in self.config.keys() else None

    def _get_db(self):
        return self.service_resolver.get_service(PersistentDictionary, config=self._db_config)

    @staticmethod
    def _get_sender_recipient_number_hash(sender, recipient=None):
        return 'messages_no::{0}:{1}'.format(sender, '' if recipient is None else recipient)

    @staticmethod
    def _get_sender_recipient_time_hash(sender, recipient=None):
        return 'messages_time::{0}:{1}'.format(sender, '' if recipient is None else recipient)

    def get_message_number(self, sender, recipient):
        key = Statistics._get_sender_recipient_number_hash(sender, recipient)

        with self._get_db() as db:
            return db.get(key, 0)

    def increment_message_number(self, sender, recipient):
        key = Statistics._get_sender_recipient_number_hash(sender, recipient)

        with self._get_db() as db:
            db.set(key, db.get(key, 0) + 1)

    def reset_message_number(self, sender, recipient=None):
        with self._get_db() as db:
            if not recipient is None:
                keys = [Statistics._get_sender_recipient_number_hash(sender, recipient), ]
            else:
                has_part = Statistics._get_sender_recipient_number_hash(sender)
                keys = list([key for key in db.keys() if key.startswith(has_part)])

            for key in keys:
                db.delete(key)

    def get_last_message_timestamp(self, sender, recipient):
        key = Statistics._get_sender_recipient_time_hash(sender, recipient)

        with self._get_db() as db:
            return db.get(key, 0)

    def update_last_message_timestamp(self, sender, recipient, timestamp=None):
        key = Statistics._get_sender_recipient_time_hash(sender, recipient)
        if timestamp is None:
            timestamp = time.time()

        with self._get_db() as db:
            db.set(key, timestamp)

    def reset_last_message_timestamp(self, sender, recipient=None):
        with self._get_db() as db:
            if not recipient is None:
                keys = [Statistics._get_sender_recipient_time_hash(sender, recipient), ]
            else:
                has_part = Statistics._get_sender_recipient_time_hash(sender)
                keys = list([key for key in db.keys() if key.startswith(has_part)])

            for key in keys:
                db.delete(key)

    def reset(self):
        with self._get_db() as db:
            for key in db.keys():
                db.delete(key)