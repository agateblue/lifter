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

from lifter.backends import elasticsearch
from lifter import adapters
from lifter import models
from lifter import exceptions

from .import mixins

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'elasticsearch')


class Scene(models.Model):

    class Meta:
        app_name = 'shakespeare'


class TestES2Backend(mixins.HTTPMixin):

    def setUp(self):
        self.store = elasticsearch.ES2Store(base_url='http://es')

    def get_data(self, path):
        with open(os.path.join(DATA_PATH, path)) as f:
            content = f.read()
        return json.loads(content)

    def test_can_build_correct_url_for_model(self):
        manager = self.store.query(Scene)
        part = manager.store.get_model_url_part()
        self.assertEqual(part, 'shakespeare/scene')

    @requests_mock.mock()
    def test_can_query_all(self, m):
        data = self.get_data('all.json')
        self.mock_request(m, 'http://es/shakespeare/scene/_search', data)
        manager = self.store.query(Scene)
        qs = manager.all()

        self.assertEqual(len(data['hits']['hits']), len(qs))
        for i, scene in enumerate(qs):
            self.assertDictEqualsModel(data['hits']['hits'][i]['_source'], scene)

    @requests_mock.mock()
    def test_can_count(self, m):
        data = self.get_data('count.json')
        self.mock_request(m, 'http://es/shakespeare/scene/_count', data)
        manager = self.store.query(Scene)

        self.assertEqual(manager.all().count(), data['count'])

    def test_can_override_number_of_returned_records(self):
        manager = self.store.query(Scene)

        qs = manager.all()[:154]
        query = qs.query
        self.assertEqual(query.window.as_slice(), slice(None, 154))

        querystring = manager.store.build_querystring(query)
        self.assertEqual(querystring, {'size': 154, 'from': 0})

    def test_can_compile_filter_eq(self):
        manager = self.store.query(Scene)
        qs = manager.filter(Scene.speaker == 'LEONTES')

        expected = {'q': 'speaker:"LEONTES"'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(qs.query.filters), expected)

    def test_can_compile_and_filters_eq(self):
        manager = self.store.query(Scene)
        qs = manager.filter(Scene.speaker == 'LEONTES', Scene.line_id == 422)

        expected = {'q': '(speaker:"LEONTES" AND line_id:422)'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(qs.query.filters), expected)

    def test_can_compile_three_filters_and_eq(self):
        manager = self.store.query(Scene)
        qs = manager.filter(Scene.speaker == 'LEONTES', Scene.line_id == 1, Scene.play == 'henry')

        expected = {'q': '(speaker:"LEONTES" AND line_id:1 AND play:"henry")'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(qs.query.filters), expected)

    def test_can_compile_three_filters_or_eq(self):
        manager = self.store.query(Scene)
        qs = manager.filter((Scene.speaker == 'LEONTES') | (Scene.line_id == 1) | (Scene.play == 'henry'))

        expected = {'q': '(speaker:"LEONTES" OR line_id:1 OR play:"henry")'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(qs.query.filters), expected)

    def test_can_compile_and_not_filters_eq(self):
        manager = self.store.query(Scene)
        qs = manager.filter(~(Scene.speaker == 'LEONTES'), Scene.line_id == 422)

        expected = {'q': '(NOT speaker:"LEONTES" AND line_id:422)'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(qs.query.filters), expected)

    def test_can_compile_and_not_filters_eq_outside(self):
        manager = self.store.query(Scene)
        query = ~(Scene.speaker == 'LEONTES') & (Scene.line_id == 422)
        qs = manager.filter(~query)

        expected = {'q': 'NOT (NOT speaker:"LEONTES" AND line_id:422)'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(qs.query.filters), expected)

    def test_can_compile_filter_gt(self):
        manager = self.store.query(Scene)
        qs = manager.filter(Scene.speaker > 'LEONTES')

        expected = {'q': 'speaker:>LEONTES'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(qs.query.filters), expected)

    def test_can_compile_filter_gte(self):
        manager = self.store.query(Scene)
        qs = manager.filter(Scene.speaker >= 'LEONTES')

        expected = {'q': 'speaker:>=LEONTES'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(qs.query.filters), expected)

    def test_can_compile_filter_lt(self):
        manager = self.store.query(Scene)
        qs = manager.filter(Scene.speaker < 'LEONTES')

        expected = {'q': 'speaker:<LEONTES'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(qs.query.filters), expected)

    def test_can_compile_filter_lte(self):
        manager = self.store.query(Scene)
        qs = manager.filter(Scene.speaker <= 'LEONTES')

        expected = {'q': 'speaker:<=LEONTES'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(qs.query.filters), expected)

    def test_can_sort_with_single_ordering(self):
        manager = self.store.query(Scene)
        qs = manager.order_by(Scene.speaker)
        expected = {'sort': 'speaker:asc    '}
        builder = elasticsearch.ES2QueryStringBuilder()

    def test_can_sort_with_multiple_orderings(self):
        manager = self.store.query(Scene)
        qs = manager.order_by(Scene.speaker, ~Scene.line_id)
        expected = {'sort': 'speaker:asc,line_id:desc'}
        builder = elasticsearch.ES2QueryStringBuilder()

        self.assertEqual(builder.build(orderings=qs.query.orderings), expected)
