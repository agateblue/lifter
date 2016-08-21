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

from lifter.backends import http
from lifter import adapters
from lifter import models
from lifter import exceptions

from . import mixins

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'db.json')


class Post(models.Model):
    pass


class TestRESTBackend(mixins.HTTPMixin):

    def setUp(self):
        self.store = http.RESTStore(base_url='http://api')

        with open(DB_PATH, 'r') as f:
            db_content = f.read()

        self.db = json.loads(db_content)


    def test_dict_adapter_works_recursively(self):
        payload = {
            'id': 1,
            'author': {
                'id': 1,
                'name': 'Roger'
            }
        }
        adapter = adapters.DictAdapter(recursive=True)
        r = adapter.parse(payload, Post)
        self.assertTrue(isinstance(r.author, models.Model))

    @requests_mock.mock()
    def test_can_query_all_instances(self, m):
        m.get('http://api/posts', text=json.dumps(self.db['posts']), headers={'Content-Type': 'application/json'},)

        manager = self.store.query(Post, adapter=adapters.DictAdapter())

        self.assertEqual(manager.count(), len(self.db['posts']))

        results = list(manager.all())

        self.assertEqual(results[0].title, self.db['posts'][0]['title'])
        self.assertEqual(results[1].title, self.db['posts'][1]['title'])

        for i, r in enumerate(results):
            self.assertTrue(isinstance(r, Post))
            self.assertDictEqualsModel(self.db['posts'][i], r)

    def test_builder_converts_filters_to_camel_case(self):
        manager = self.store.query(Post, adapter=adapters.DictAdapter())
        url = 'http://test'

        query = manager.filter(Post.author_id == 1).query
        request = manager.store.build_request(url, query, Post)
        self.assertEqual(request.url, 'http://test/?authorId=1')

    def test_adapters_converts_attributes_to_snake_case(self):
        payload = {
            'authorId': 3,
            'id': 1,
        }
        adapter = adapters.DictAdapter()
        instance = adapter.parse(payload, Post)
        self.assertEqual(instance.author_id, 3)

    def test_simple_querystring_builder(self):
        builder = http.SimpleQueryStringBuilder()
        q = Post.id == 1
        d = builder.build(q)
        expected = {
            'id': [1]
        }

        self.assertEqual(d, expected)

    def test_simple_querystring_builder_multiple_args(self):
        builder = http.SimpleQueryStringBuilder()
        q = (Post.published == True) & (Post.author == 'Kurt')
        d = builder.build(q)
        expected = {
            'published': [True],
            'author': ['Kurt'],
        }

        self.assertEqual(d, expected)

    def test_unsupported_queries(self):
        builder = http.SimpleQueryStringBuilder()

        with self.assertRaises(exceptions.UnsupportedQuery):
            builder.build(Post.id >= 1)

        with self.assertRaises(exceptions.UnsupportedQuery):
            builder.build(~(Post.id == 1))

        with self.assertRaises(exceptions.UnsupportedQuery):
            q = (Post.id == 1) | (Post.id == 2)
            builder.build(q)

    @requests_mock.mock()
    def test_can_query_single_instance(self, m):
        m.get('http://api/posts?id=1', text=json.dumps([self.db['posts'][0]]), headers={'Content-Type': 'application/json'},)

        manager = self.store.query(Post, adapter=adapters.DictAdapter())

        result = manager.all().get(id=1)

        self.assertDictEqualsModel(self.db['posts'][0], result)

    @requests_mock.mock()
    def test_raise_error_on_get_with_multiple_results(self, m):
        m.get('http://api/posts?author=typicode', text=json.dumps(self.db['posts']), headers={'Content-Type': 'application/json'},)

        manager = self.store.query(Post, adapter=adapters.DictAdapter())

        with self.assertRaises(exceptions.MultipleObjectsReturned):
            result = manager.all().get(author='typicode')

    @requests_mock.mock()
    def test_400_error_raise_querry_error(self, m):
        m.get('http://api/posts', text='', status_code=400)
        manager = self.store.query(Post, adapter=adapters.DictAdapter())

        with self.assertRaises(exceptions.BadQuery):
            result = manager.all().get(id=1)

    @requests_mock.mock()
    def test_500_error_raise_store_error(self, m):
        m.get('http://api/posts', text='', status_code=500)
        manager = self.store.query(Post, adapter=adapters.DictAdapter())

        with self.assertRaises(exceptions.StoreError):
            result = manager.all().get(id=1)
