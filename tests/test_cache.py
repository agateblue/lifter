#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import datetime
import unittest
import mock
import json
import requests
import requests_mock

from lifter import caches
from lifter import models
from lifter import exceptions
from lifter import query
from lifter.backends.python import IterableStore

class TModel(models.Model):

    class Meta:
        name = 'test_model'
        app_name = 'test'

    def __repr__(self):
        return self.name

class TestCache(unittest.TestCase):
    def setUp(self):
        self.cache = caches.DummyCache()

        PARENTS = [
                TModel(name='parent_1'),
                TModel(name='parent_2'),
            ]
        OBJECTS = [
            TModel(name='test_1', order=2, a=1, parent=PARENTS[0], label='alabama', surname='Mister T'),
            TModel(name='test_2', order=3, a=1, parent=PARENTS[0], label='arkansas', surname='Colonel'),
            TModel(name='test_3', order=1, a=2, parent=PARENTS[1], label='texas', surname='Lincoln'),
            TModel(name='test_4', order=4, a=2, parent=PARENTS[1], label='washington', surname='clint'),
        ]
        self.store = IterableStore(OBJECTS, identifier='test', cache=self.cache)
        self.manager = self.store.query(TModel)

    def test_store_uses_store_model_app_name_and_hashed_query_for_cache_key(self):
        store = self.manager.store
        query = self.manager.all().query
        cache_parts = [
            self.store.identifier,
            TModel._meta.app_name,
            TModel._meta.name,
            store.hash_query(query),
        ]
        expected = ':'.join(cache_parts)
        self.assertEqual(
            store.get_cache_key(query, TModel), expected)

    def test_store_tries_to_return_from_cache_before_executing_query(self):
        with mock.patch('lifter.store.Store.get_from_cache', side_effect=exceptions.NotInCache()) as m:
            qs = self.manager.all()
            query = qs.query
            list(qs)
            m.assert_called_with(query, TModel)

    def test_store_stores_result_in_cache_when_queyr_is_executed(self):
        r = self.manager.count()
        cache_key = list(self.cache._data.keys())[0]
        expires_on, value = self.cache._data[cache_key]
        self.assertEqual(value, r)

    @mock.patch('lifter.caches.Cache._get')
    def test_can_disable_cache(self, mocked):
        with self.cache.disable():
            r = self.manager.count()
            self.manager.count()
            mocked.assert_not_called()

class TestDummyCache(unittest.TestCase):

    def setUp(self):
        self.cache = caches.DummyCache()

    def test_can_store_value(self):
        self.cache.set('key', 'value')
        self.assertEqual(self.cache.get('key'), 'value')

    def test_can_get_or_default(self):
        self.assertEqual(self.cache.get('key', 'default'), 'default')

    def test_can_get_or_set(self):
        r = self.cache.get_or_set('key', 'value')
        self.assertEqual(r, 'value')

    def test_can_pass_callable_to_set(self):
        f = lambda: 'yolo'

        r = self.cache.get_or_set('key', f)
        self.assertEqual(r, 'yolo')

    def test_can_provide_timeout(self):
        now = datetime.datetime.now()
        self.cache.set('key', 'value', 3600)
        with mock.patch('lifter.caches.Cache.get_now', return_value=now + datetime.timedelta(seconds=3599)):
            self.assertEqual(self.cache.get('key'), 'value')

        with mock.patch('lifter.caches.Cache.get_now', return_value=now + datetime.timedelta(seconds=3601)):
            self.assertEqual(self.cache.get('key'), None)
