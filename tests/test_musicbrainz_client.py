#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import datetime
import unittest
import requests
import requests_mock
# import mock
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

from . import musicbrainz

class TestMusicBrainzBackend(unittest.TestCase):
    def setUp(self):
        self.adapter = requests_mock.Adapter()
        self.session = requests.Session()
        self.session.mount('mock', self.adapter)
        self.client = musicbrainz.Client(session=self.session, protocol='mock')


    def test_can_search_release(self):
        with open(os.path.join(DATA_DIR, 'musicbrainz_release_search.xml'), 'rb') as f:
            self.adapter.register_uri('GET', '/ws/2/release', body=f)
            results = self.client.releases.search('carpenter')
        self.assertEqual(len(results), 4)

        self.assertEqual(results[0].title, 'Carpenter')
        self.assertEqual(results[0].date, '2015-04-07')
