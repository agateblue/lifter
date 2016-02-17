#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lifter
----------------------------------

Tests for `lifter` module.
"""

import unittest

import lifter


class TestObject(object):
    def __init__(self, name, **kwargs):
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return self.name

class TestManagers(unittest.TestCase):
    PARENTS = [
        TestObject(name='parent_1'),
        TestObject(name='parent_2'),
    ]
    OBJECTS = [
        TestObject(name='test_1', order=2, a=1, parent=PARENTS[0]),
        TestObject(name='test_2', order=3, a=1, parent=PARENTS[0]),
        TestObject(name='test_3', order=1, a=2, parent=PARENTS[1]),
        TestObject(name='test_4', order=4, a=2, parent=PARENTS[1]),
    ]

    DICTS = [o.__dict__ for o in OBJECTS]

    def setUp(self):
        self.manager = lifter.load(self.OBJECTS)
        self.dict_manager = lifter.load(self.DICTS)

    def test_default_order(self):
        self.assertEqual(list(self.manager.all()), self.OBJECTS)
        self.assertEqual(list(self.dict_manager.all()), self.DICTS)

    def test_can_get_using_attribute(self):
        self.assertEqual(self.manager.get(name='test_1'), self.OBJECTS[0])
        self.assertEqual(self.dict_manager.get(name='test_1'), self.DICTS[0])

    def test_can_filter(self):
        self.assertEqual(self.manager.filter(a=1), self.OBJECTS[:2])

    def test_can_combine_filters(self):
        self.assertEqual(self.manager.filter(a=1, name='test_2'), self.OBJECTS[1:2])
        self.assertEqual(self.manager.filter(a=1).filter(name='test_2'), self.OBJECTS[1:2])

        self.assertEqual(self.dict_manager.filter(a=1, name='test_2'), self.DICTS[1:2])
        self.assertEqual(self.dict_manager.filter(a=1).filter(name='test_2'), self.DICTS[1:2])

    def test_related_lookups(self):
        self.assertEqual(self.manager.filter(parent__name='parent_1'), self.OBJECTS[:2])
        self.assertEqual(self.manager.exclude(parent__name='parent_1'), self.OBJECTS[2:])
        self.assertEqual(self.manager.get(parent__name='parent_1', order=2), self.OBJECTS[0])

        self.assertEqual(self.dict_manager.filter(parent__name='parent_1'), self.DICTS[:2])
        self.assertEqual(self.dict_manager.exclude(parent__name='parent_1'), self.DICTS[2:])
        self.assertEqual(self.dict_manager.get(parent__name='parent_1', order=2), self.DICTS[0])

    def test_can_exclude(self):
        self.assertEqual(self.manager.exclude(a=1), self.OBJECTS[2:])

        self.assertEqual(self.dict_manager.exclude(a=1), self.DICTS[2:])

    def test_can_combine_exclude(self):
        self.assertEqual(self.manager.exclude(a=1).exclude(name='test_4'), self.OBJECTS[2:3])
        self.assertEqual(self.manager.exclude(a=2, name='test_4'), self.OBJECTS[:3])

        self.assertEqual(self.dict_manager.exclude(a=1).exclude(name='test_4'), self.DICTS[2:3])
        self.assertEqual(self.dict_manager.exclude(a=2, name='test_4'), self.DICTS[:3])

    def test_can_count(self):
        self.assertEqual(self.manager.filter(a=1).count(), 2)

        self.assertEqual(self.dict_manager.filter(a=1).count(), 2)

    def test_first(self):
        self.assertIsNone(self.manager.filter(a=123).first())
        self.assertIsNotNone(self.manager.filter(a=1).first())

        self.assertIsNone(self.dict_manager.filter(a=123).first())
        self.assertIsNotNone(self.dict_manager.filter(a=1).first())

    def test_ordering(self):
        self.assertEqual(self.manager.order_by('order')[:2], [self.OBJECTS[2], self.OBJECTS[0]])
        self.assertEqual(self.manager.order_by('-order')[:2], [self.OBJECTS[3], self.OBJECTS[1]])

        self.assertEqual(self.dict_manager.order_by('order')[:2], [self.DICTS[2], self.DICTS[0]])
        self.assertEqual(self.dict_manager.order_by('-order')[:2], [self.DICTS[3], self.DICTS[1]])

    def test_last(self):
        self.assertIsNone(self.manager.filter(a=123).last())
        self.assertIsNotNone(self.manager.filter(a=1).last())

        self.assertIsNone(self.dict_manager.filter(a=123).last())
        self.assertIsNotNone(self.dict_manager.filter(a=1).last())

    def test_exists(self):
        self.assertFalse(self.manager.filter(a=123).exists())
        self.assertTrue(self.manager.filter(a=1).exists())

        self.assertFalse(self.dict_manager.filter(a=123).exists())
        self.assertTrue(self.dict_manager.filter(a=1).exists())

    def test_get_raise_exception_on_multiple_objects_returned(self):
        with self.assertRaises(lifter.MultipleObjectsReturned):
            self.manager.get(a=1)

        with self.assertRaises(lifter.MultipleObjectsReturned):
            self.dict_manager.get(a=1)

    def test_get_raise_exception_on_does_not_exist(self):
        with self.assertRaises(lifter.DoesNotExist):
            self.manager.get(a=123)

        with self.assertRaises(lifter.DoesNotExist):
            self.dict_manager.get(a=123)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
