#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lifter
----------------------------------

Tests for `lifter` module.
"""

import random
import sys
import unittest

import lifter.models
import lifter.aggregates
import lifter.exceptions
import lifter.lookups
from lifter.backends.python import IterableStore


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
        TestObject(name='test_1', order=2, a=1, parent=PARENTS[0], label='alabama', surname='Mister T'),
        TestObject(name='test_2', order=3, a=1, parent=PARENTS[0], label='arkansas', surname='Colonel'),
        TestObject(name='test_3', order=1, a=2, parent=PARENTS[1], label='texas', surname='Lincoln'),
        TestObject(name='test_4', order=4, a=2, parent=PARENTS[1], label='washington', surname='clint'),
    ]

    DICTS = [o.__dict__ for o in OBJECTS]

    def setUp(self):
        class TestModel(lifter.models.Model):
            pass
        self.manager = IterableStore(self.OBJECTS).query(TestModel)
        self.dict_manager = IterableStore(self.DICTS).query(TestModel)

class TestQueries(TestBase):

    def test_default_order(self):
        self.assertEqual(list(self.manager.all()), self.OBJECTS)
        self.assertEqual(list(self.dict_manager.all()), self.DICTS)

    def test_can_get_using_attribute(self):
        self.assertEqual(self.manager.all().get(name='test_1'), self.OBJECTS[0])
        self.assertEqual(self.dict_manager.all().get(name='test_1'), self.DICTS[0])

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
        self.assertEqual(self.manager.all().get(parent__name='parent_1', order=2), self.OBJECTS[0])

        self.assertEqual(self.dict_manager.filter(parent__name='parent_1'), self.DICTS[:2])
        self.assertEqual(self.dict_manager.exclude(parent__name='parent_1'), self.DICTS[2:])
        self.assertEqual(self.dict_manager.all().get(parent__name='parent_1', order=2), self.DICTS[0])

    def test_exception_raised_on_missing_attr(self):
        with self.assertRaises(lifter.exceptions.MissingField):
            self.manager.filter(x="y").count()
        with self.assertRaises(lifter.exceptions.MissingField):
            self.dict_manager.filter(x="y").count()

    # def test_can_check_nested_iterables(self):
    #     users = [
    #         {
    #             'name': 'Kurt',
    #             'tags': [
    #                 {'name': 'nice'},
    #                 {'name': 'friendly'},
    #             ]
    #         },
    #         {
    #             'name': 'Bill',
    #             'tags': [
    #                 {'name': 'friendly'},
    #             ]
    #         },
    #     ]
    #     manager = lifter.load(users)
    #     self.assertNotIn(users[1], manager.filter(tags__name='nice'))
    #     self.assertRaises(ValueError, manager.filter, tags__x='y')
    #
    #     companies = [
    #         {
    #             'name': 'blackbooks',
    #             'employees': [
    #                 {
    #                     'name': 'Manny',
    #                     'tags': [
    #                         {'name': 'nice'},
    #                         {'name': 'friendly'},
    #                     ]
    #                 }
    #             ]
    #         },
    #         {
    #             'name': 'community',
    #             'employees': [
    #                 {
    #                     'name': 'Britta',
    #                     'tags': [
    #                         {'name': 'activist'},
    #                     ]
    #                 }
    #             ]
    #         }
    #     ]
    #     manager = lifter.load(companies)
    #     self.assertNotIn(companies[1], manager.filter(employees__tags__name='friendly'))

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

    @unittest.skip('If someone find a proper way to unittest random ordering, contribution is welcome')
    def test_random_ordering(self):
        is_py3 = sys.version_info >= (3, 2)
        random.seed(0)
        random_ordered_0 = self.dict_manager.order_by('?')[:2]
        if is_py3:
            self.assertEqual(random_ordered_0, [self.DICTS[3], self.DICTS[1]])
        else:
            self.assertEqual(random_ordered_0, [self.DICTS[3], self.DICTS[2]])
        random.seed(1)
        random_ordered_1 = self.dict_manager.order_by('?')[:2]
        if is_py3:
            self.assertEqual(random_ordered_1, [self.DICTS[1], self.DICTS[2]])
        else:
            self.assertEqual(random_ordered_1, [self.DICTS[0], self.DICTS[2]])

        self.assertNotEqual(random_ordered_0, random_ordered_1)

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
        with self.assertRaises(lifter.exceptions.MultipleObjectsReturned):
            self.manager.all().get(a=1)

        with self.assertRaises(lifter.exceptions.MultipleObjectsReturned):
            self.dict_manager.all().get(a=1)

    def test_get_raise_exception_on_does_not_exist(self):
        with self.assertRaises(lifter.exceptions.DoesNotExist):
            self.manager.all().get(a=123)

        with self.assertRaises(lifter.exceptions.DoesNotExist):
            self.dict_manager.all().get(a=123)

    def test_can_filter_using_callable(self):
        self.assertEqual(self.manager.filter(order__test=lambda v: v in [1, 3]), [self.OBJECTS[1], self.OBJECTS[2]])

        self.assertEqual(self.dict_manager.filter(order__test=lambda v: v in [1, 3]), [self.DICTS[1], self.DICTS[2]])

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
        self.assertEqual(self.manager.all().values_list('a', flat=True), [1, 1, 2, 2])
        self.assertEqual(self.manager.all().values_list('a', flat=True).distinct(), [1, 2])
        self.assertEqual(self.manager.all().values_list('parent', flat=True).distinct(), self.PARENTS)

class TestLookups(TestBase):
    def test_gt(self):
        self.assertEqual(self.manager.filter(order__gt=3), [self.OBJECTS[3]])

    def test_gte(self):
        self.assertEqual(self.manager.filter(order__gte=3), [self.OBJECTS[1], self.OBJECTS[3]])

    def test_lt(self):
        self.assertEqual(self.manager.filter(order__lt=3), [self.OBJECTS[0], self.OBJECTS[2]])

    def test_lte(self):
        self.assertEqual(self.manager.filter(order__lte=3), [self.OBJECTS[0], self.OBJECTS[1], self.OBJECTS[2]])

    def test_startswith(self):
        self.assertEqual(self.manager.filter(label__startswith='a'), [self.OBJECTS[0], self.OBJECTS[1]])

    def test_endswith(self):
        self.assertEqual(self.manager.filter(label__endswith='s'), [self.OBJECTS[1], self.OBJECTS[2]])

    def test_value_in(self):
        self.assertEqual(self.manager.filter(label__value_in=['alabama', 'arkansas']), [self.OBJECTS[0], self.OBJECTS[1]])

    def test_range(self):
        self.assertEqual(self.manager.filter(order__value_range=(2, 3)), [self.OBJECTS[0], self.OBJECTS[1]])

    def test_istartswith(self):
        self.assertEqual(self.manager.filter(surname__istartswith='c'), [self.OBJECTS[1], self.OBJECTS[3]])

    def test_iendswith(self):
        self.assertEqual(self.manager.filter(surname__iendswith='t'), [self.OBJECTS[0], self.OBJECTS[3]])

    def test_contains(self):
        self.assertEqual(self.manager.filter(surname__contains='Lin'), [self.OBJECTS[2]])

    def test_icontains(self):
        self.assertEqual(self.manager.filter(surname__icontains='lin'), [self.OBJECTS[2], self.OBJECTS[3]])

class TestAggregation(TestBase):
    def test_sum(self):
        self.assertEqual(self.manager.aggregate(lifter.aggregates.Sum('a')), {'a__sum': 6})
        self.assertEqual(self.manager.aggregate(total=lifter.aggregates.Sum('a')), {'total': 6})

    def test_min(self):
        self.assertEqual(self.manager.aggregate(lifter.aggregates.Min('a')), {'a__min': 1})

    def test_max(self):
        self.assertEqual(self.manager.aggregate(lifter.aggregates.Max('a')), {'a__max': 2})

    def test_avg(self):
        self.assertEqual(self.manager.aggregate(lifter.aggregates.Avg('a')), {'a__avg': 1.5})

    def test_flat(self):
        self.assertEqual(self.manager.aggregate(lifter.aggregates.Avg('a'), flat=True), [1.5])

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
