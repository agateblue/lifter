#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import datetime
import unittest
# import mock
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'log.sample')

from lifter.backends import filesystem
from lifter.models import Model
from lifter.parsers import RegexParser

LogEntry = Model('LogEntry')

class Parser(RegexParser):
    regex='(?P<level>.*) - (?P<date>.*) - (?P<message>.*)'

    def clean_date(self, value):
        year, month, day = [int(part) for part in value.split('/')]
        return datetime.date(year, month, day)


class TestFileBackend(unittest.TestCase):
    def setUp(self):
        self.manager = filesystem.FileManager(model=LogEntry, path=DATA_PATH, parser=Parser())

    def test_manager_can_load_objects_from_file(self):
        values = self.manager.get_values()
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
        self.assertEqual(self.manager.all().count(), 3)
        self.assertEqual(self.manager.filter(level='ERROR').first().message, 'Something BAD happened')
        
