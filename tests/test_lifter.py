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

class TestBase(unittest.TestCase):
    PARENTS = [
        TestObject(name='parent_1'),
        TestObject(name='parent_2'),
    ]
    OBJECTS = [
        TestObject(name='test_1', order=2, a=1, parent=PARENTS[0], label='alabama'),
        TestObject(name='test_2', order=3, a=1, parent=PARENTS[0], label='arkansas'),
        TestObject(name='test_3', order=1, a=2, parent=PARENTS[1], label='texas'),
        TestObject(name='test_4', order=4, a=2, parent=PARENTS[1], label='washington'),
    ]

    DICTS = [o.__dict__ for o in OBJECTS]

    def setUp(self):
        self.manager = lifter.load(self.OBJECTS)
        self.dict_manager = lifter.load(self.DICTS)

class TestQueries(TestBase):

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

    def test_can_filter_using_callable(self):
        self.assertEqual(self.manager.filter(order=lambda v: v in [1, 3]), [self.OBJECTS[1], self.OBJECTS[2]])

        self.assertEqual(self.dict_manager.filter(order=lambda v: v in [1, 3]), [self.DICTS[1], self.DICTS[2]])

    def test_values(self):
        expected = [
            {'order': 2},
            {'order': 3},
        ]
        self.assertEqual(self.manager.filter(a=1).values('order'), expected)
        self.assertEqual(self.dict_manager.filter(a=1).values('order'), expected)

        expected = [
            {'order': 2, 'a': 1},
            {'order': 3, 'a': 1},
        ]
        self.assertEqual(self.manager.filter(a=1).values('order', 'a'), expected)
        self.assertEqual(self.dict_manager.filter(a=1).values('order', 'a'), expected)

    def test_values_list(self):
        expected = [2, 3]
        self.assertEqual(self.manager.filter(a=1).values_list('order', flat=True), expected)
        self.assertEqual(self.dict_manager.filter(a=1).values_list('order', flat=True), expected)

        expected = [
            (2, 1),
            (3, 1),
        ]
        self.assertEqual(self.manager.filter(a=1).values_list('order', 'a'), expected)
        self.assertEqual(self.dict_manager.filter(a=1).values_list('order', 'a'), expected)

    def test_distinct(self):
        self.assertEqual(self.manager.values_list('a', flat=True), [1, 1, 2, 2])
        self.assertEqual(self.manager.values_list('a', flat=True).distinct(), [1, 2])
        self.assertEqual(self.manager.values_list('parent', flat=True).distinct(), self.PARENTS)

class TestLookups(TestBase):
    def test_gt(self):
        self.assertEqual(self.manager.filter(order=lifter.lookups.gt(3)), [self.OBJECTS[3]])

    def test_gte(self):
        self.assertEqual(self.manager.filter(order=lifter.lookups.gte(3)), [self.OBJECTS[1], self.OBJECTS[3]])

    def test_lt(self):
        self.assertEqual(self.manager.filter(order=lifter.lookups.lt(3)), [self.OBJECTS[0], self.OBJECTS[2]])

    def test_lte(self):
        self.assertEqual(self.manager.filter(order=lifter.lookups.lte(3)), [self.OBJECTS[0], self.OBJECTS[1], self.OBJECTS[2]])

    def test_startswith(self):
        self.assertEqual(self.manager.filter(label=lifter.lookups.startswith('a')), [self.OBJECTS[0], self.OBJECTS[1]])

    def test_startswith(self):
        self.assertEqual(self.manager.filter(label=lifter.lookups.endswith('s')), [self.OBJECTS[1], self.OBJECTS[2]])

    def test_value_in(self):
        self.assertEqual(self.manager.filter(label=lifter.lookups.value_in(['alabama', 'arkansas'])), [self.OBJECTS[0], self.OBJECTS[1]])

    def test_range(self):
        self.assertEqual(self.manager.filter(order=lifter.lookups.value_range(2, 3)), [self.OBJECTS[0], self.OBJECTS[1]])


class TestAggregation(TestBase):
    def test_sum(self):
        self.assertEqual(self.manager.aggregate(lifter.Sum('a')), {'a__sum': 6})
        self.assertEqual(self.manager.aggregate(total=lifter.Sum('a')), {'total': 6})

    def test_min(self):
        self.assertEqual(self.manager.aggregate(lifter.Min('a')), {'a__min': 1})

    def test_max(self):
        self.assertEqual(self.manager.aggregate(lifter.Max('a')), {'a__max': 2})

    def test_avg(self):
        self.assertEqual(self.manager.aggregate(lifter.Avg('a')), {'a__avg': 1.5})


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
