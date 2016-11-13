#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import datetime
import unittest
# import mock
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'log.sample')

from lifter.backends import document
from lifter.models import Model
from lifter import adapters, parsers


class LogEntry(Model):
    pass


class Adapter(adapters.RegexAdapter):
    regex = '(?P<level>.*) - (?P<date>.*) - (?P<message>.*)'

    def clean_date(self, data, value, model, field):
        year, month, day = [int(part) for part in value.split(
        '/')]
        return datetime.date(year, month, day)


class TestDocumentBackend(unittest.TestCase):
    def setUp(self):
        self.store = document.DocumentStore(url='file://' + DATA_PATH)

    def test_manager_can_load_objects_from_file(self):
        manager = self.store.query(LogEntry, adapter=Adapter())
        values = list(manager.all())
        self.assertEqual(len(values), 3)

        self.assertEqual(values[0].level, 'INFO')
        self.assertEqual(values[0].date, datetime.date(2016, 3, 23))
        self.assertEqual(values[0].message, 'Something happened')

        self.assertEqual(values[1].level, 'ERROR')
        self.assertEqual(values[1].date, datetime.date(2016, 3, 23))
        self.assertEqual(values[1].message, 'Something BAD happened')

        self.assertEqual(values[2].level, 'DEBUG')
        self.assertEqual(values[2].date, datetime.date(2016, 3, 21))
        self.assertEqual(values[2].message, 'Hello there')

    def test_can_filter_data_from_file_backend(self):
        manager = self.store.query(LogEntry, adapter=Adapter())
        self.assertEqual(manager.all().count(), 3)
        self.assertEqual(manager.filter(level='ERROR').count(), 1)
        self.assertEqual(manager.filter(level='ERROR').first().message, 'Something BAD happened')

    def test_can_use_custom_parser(self):

        class DummyParser(parsers.Parser):
            def parse(self, content):
                return content.split('\n')

        parser = DummyParser()
        store = document.DocumentStore(url='file://' + DATA_PATH, parser=parser)

        manager = self.store.query(LogEntry, adapter=Adapter())

        values = list(manager.all())
        self.assertEqual(len(values), 3)
