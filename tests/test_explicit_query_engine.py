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
import mock
import lifter.models


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
        self.manager = lifter.load(self.OBJECTS)
        self.dict_manager = lifter.load(self.DICTS)

TestModel = lifter.models.Model('TestModel')

class TestQueries(TestBase):

    def test_model(self):
        manager = TestModel.load(self.OBJECTS)
        self.assertEqual(manager.filter(TestModel.a == 1), self.OBJECTS[:2])

    def test_can_match_object(self):
        query = TestModel.order == 1
        self.assertTrue(query.match(self.OBJECTS[2]))
        self.assertFalse(query.match(self.OBJECTS[3]))

    def test_default_order(self):
        self.assertEqual(list(self.manager.all()), self.OBJECTS)
        self.assertEqual(list(self.dict_manager.all()), self.DICTS)

    def test_can_get_using_attribute(self):
        self.assertEqual(self.manager.get(TestModel.name == 'test_1'), self.OBJECTS[0])
        self.assertEqual(self.dict_manager.get(TestModel.name == 'test_1'), self.DICTS[0])

    def test_can_filter(self):
        self.assertEqual(self.manager.filter(TestModel.a == 1), self.OBJECTS[:2])

    def test_get_exclude_and_filter_combine_queries_to_and_by_default(self):
        self.assertEqual(self.manager.get(TestModel.order > 2, TestModel.a == 2), self.OBJECTS[3])
        self.assertEqual(self.manager.filter(TestModel.order > 2, TestModel.a == 2), [self.OBJECTS[3]])
        self.assertEqual(self.manager.exclude(TestModel.order > 2, TestModel.a == 2), self.OBJECTS[:3])

    def test_queryset_is_lazy(self):
        with mock.patch('lifter.query.QuerySet._fetch_all') as fetch:
            qs = self.manager.all().filter(TestModel.order == 3)
            fetch.assert_not_called()
            self.assertFalse(qs._populated)
            self.assertEqual(qs._data, [])

        self.assertEqual(qs, [self.OBJECTS[1]])

        with mock.patch('lifter.query.QuerySet._fetch_all') as fetch:
            self.assertEqual(qs, [self.OBJECTS[1]])
            self.assertEqual(qs, [self.OBJECTS[1]])
            self.assertEqual(qs, [self.OBJECTS[1]])
            self.assertTrue(qs._populated)
            fetch.assert_not_called()


    def test_can_combine_filters(self):
        self.assertEqual(self.manager.filter((TestModel.a == 1) & (TestModel.name == 'test_2')), self.OBJECTS[1:2])
        self.assertEqual(self.manager.filter(TestModel.a == 1).filter(TestModel.name == 'test_2'), self.OBJECTS[1:2])

        self.assertEqual(self.dict_manager.filter((TestModel.a == 1) & (TestModel.name == 'test_2')), self.DICTS[1:2])
        self.assertEqual(self.dict_manager.filter(TestModel.a == 1).filter(TestModel.name == 'test_2'), self.DICTS[1:2])

    @mock.patch('lifter.query.QuerySet.iterator')
    def test_queries_combine_to_a_single_one(self, mocked_iterator):
        queryset = self.manager.filter(TestModel.a == 1).filter(TestModel.order == 1)
        queryset.count()
        self.assertEqual(mocked_iterator.call_count, 1)

    def test_can_exclude(self):
        self.assertEqual(self.manager.exclude(TestModel.a == 1), self.OBJECTS[2:])
        self.assertEqual(self.dict_manager.exclude(TestModel.a == 1), self.DICTS[2:])

    def test_can_combine_exclude(self):
        self.assertEqual(self.manager.exclude(TestModel.a == 1).exclude(TestModel.name == 'test_4'), self.OBJECTS[2:3])
        self.assertEqual(self.manager.exclude((TestModel.a == 2) & (TestModel.name == 'test_4')), self.OBJECTS[:3])

        self.assertEqual(self.dict_manager.exclude(TestModel.a == 1).exclude(TestModel.name == 'test_4'), self.DICTS[2:3])
        self.assertEqual(self.dict_manager.exclude((TestModel.a == 2) & (TestModel.name == 'test_4')), self.DICTS[:3])

    def test_related_lookups(self):
        self.assertEqual(self.manager.filter(TestModel.parent.name == 'parent_1'), self.OBJECTS[:2])
        self.assertEqual(self.manager.exclude(TestModel.parent.name == 'parent_1'), self.OBJECTS[2:])
        self.assertEqual(self.manager.get((TestModel.parent.name == 'parent_1') & (TestModel.order == 2)), self.OBJECTS[0])

        self.assertEqual(self.dict_manager.filter(TestModel.parent.name == 'parent_1'), self.DICTS[:2])
        self.assertEqual(self.dict_manager.exclude(TestModel.parent.name == 'parent_1'), self.DICTS[2:])
        self.assertEqual(self.dict_manager.get((TestModel.parent.name == 'parent_1') & (TestModel.order == 2)), self.DICTS[0])


    def test_exception_raised_on_missing_attr(self):
        with self.assertRaises(lifter.exceptions.MissingAttribute):
            list(self.manager.filter(TestModel.x == "y"))
        with self.assertRaises(lifter.exceptions.MissingAttribute):
            list(self.dict_manager.filter(TestModel.x == "y"))

    def test_can_count(self):
        self.assertEqual(self.manager.filter(TestModel.a == 1).count(), 2)

        self.assertEqual(self.dict_manager.filter(TestModel.a == 1).count(), 2)

    def test_first(self):
        self.assertIsNone(self.manager.filter(TestModel.a == 123).first())
        self.assertIsNotNone(self.manager.filter(TestModel.a == 1).first())

        self.assertIsNone(self.dict_manager.filter(TestModel.a == 123).first())
        self.assertIsNotNone(self.dict_manager.filter(TestModel.a == 1).first())

    def test_last(self):
        self.assertIsNone(self.manager.filter(TestModel.a == 123).last())
        self.assertIsNotNone(self.manager.filter(TestModel.a == 1).last())

        self.assertIsNone(self.dict_manager.filter(TestModel.a == 123).last())
        self.assertIsNotNone(self.dict_manager.filter(TestModel.a == 1).last())

    def test_ordering(self):
        TestModel = lifter.models.Model('TestModel')
        self.assertEqual(self.manager.order_by(TestModel.order)[:2], [self.OBJECTS[2], self.OBJECTS[0]])
        self.assertEqual(self.manager.order_by(~TestModel.order)[:2], [self.OBJECTS[3], self.OBJECTS[1]])

        self.assertEqual(self.dict_manager.order_by(TestModel.order)[:2], [self.DICTS[2], self.DICTS[0]])
        self.assertEqual(self.dict_manager.order_by(~TestModel.order)[:2], [self.DICTS[3], self.DICTS[1]])

    def test_ordering_using_multiple_paths(self):
        TestModel = lifter.models.Model('TestModel')
        p1 = TestModel.a
        p2 = TestModel.order
        self.assertEqual(self.manager.order_by(p1, p2)[:2], [self.OBJECTS[0], self.OBJECTS[1]])
        self.assertEqual(self.manager.order_by(~p1, p2)[:2], [self.OBJECTS[2], self.OBJECTS[3]])
        self.assertEqual(self.manager.order_by(p1, ~p2)[:2], [self.OBJECTS[1], self.OBJECTS[0]])
        self.assertEqual(self.manager.order_by(~p1, ~p2)[:2], [self.OBJECTS[3], self.OBJECTS[2]])

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

    def test_exists(self):
        self.assertFalse(self.manager.filter(TestModel.a == 123).exists())
        self.assertTrue(self.manager.filter(TestModel.a == 1).exists())

        self.assertFalse(self.dict_manager.filter(TestModel.a == 123).exists())
        self.assertTrue(self.dict_manager.filter(TestModel.a == 1).exists())

    def test_get_raise_exception_on_multiple_objects_returned(self):
        with self.assertRaises(lifter.MultipleObjectsReturned):
            self.manager.get(TestModel.a == 1)

        with self.assertRaises(lifter.MultipleObjectsReturned):
            self.dict_manager.get(TestModel.a == 1)

    def test_get_raise_exception_on_does_not_exist(self):
        with self.assertRaises(lifter.DoesNotExist):
            self.manager.get(TestModel.a == 123)

        with self.assertRaises(lifter.DoesNotExist):
            self.dict_manager.get(TestModel.a == 123)

    def test_can_filter_using_callable(self):
        self.assertEqual(self.manager.filter(TestModel.order.test(lambda v: v in [1, 3])), [self.OBJECTS[1], self.OBJECTS[2]])

        self.assertEqual(self.dict_manager.filter(TestModel.order.test(lambda v: v in [1, 3])), [self.DICTS[1], self.DICTS[2]])

    def test_values(self):
        expected = [
            {'order': 2},
            {'order': 3},
        ]
        self.assertEqual(self.manager.filter(TestModel.a == 1).values(TestModel.order), expected)
        self.assertEqual(self.dict_manager.filter(TestModel.a == 1).values(TestModel.order), expected)

        expected = [
            {'order': 2, 'a': 1},
            {'order': 3, 'a': 1},
        ]
        self.assertEqual(self.manager.filter(TestModel.a == 1).values(TestModel.order, TestModel.a), expected)
        self.assertEqual(self.dict_manager.filter(TestModel.a == 1).values(TestModel.order, TestModel.a), expected)

    def test_values_list(self):
        expected = [2, 3]
        self.assertEqual(self.manager.filter(TestModel.a == 1).values_list(TestModel.order, flat=True), expected)
        self.assertEqual(self.dict_manager.filter(TestModel.a == 1).values_list(TestModel.order, flat=True), expected)

        expected = [
            (2, 1),
            (3, 1),
        ]
        self.assertEqual(self.manager.filter(TestModel.a == 1).values_list(TestModel.order, TestModel.a), expected)
        self.assertEqual(self.dict_manager.filter(TestModel.a == 1).values_list(TestModel.order, TestModel.a), expected)

    def test_distinct(self):
        self.assertEqual(self.manager.values_list(TestModel.a, flat=True), [1, 1, 2, 2])
        self.assertEqual(self.manager.values_list(TestModel.a, flat=True).distinct(), [1, 2])
        self.assertEqual(self.manager.values_list(TestModel.parent, flat=True).distinct(), self.PARENTS)
    #
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

class TestLookups(TestBase):
    def test_gt(self):
        self.assertEqual(self.manager.filter(TestModel.order > 3), [self.OBJECTS[3]])

    def test_gte(self):
        self.assertEqual(self.manager.filter(TestModel.order >= 3), [self.OBJECTS[1], self.OBJECTS[3]])

    def test_lt(self):
        self.assertEqual(self.manager.filter(TestModel.order < 3), [self.OBJECTS[0], self.OBJECTS[2]])

    def test_lte(self):
        self.assertEqual(self.manager.filter(TestModel.order <= 3), [self.OBJECTS[0], self.OBJECTS[1], self.OBJECTS[2]])

    def test_startswith(self):
        self.assertEqual(self.manager.filter(TestModel.label.test(lifter.startswith('a'))),
                        [self.OBJECTS[0], self.OBJECTS[1]])

    def test_endswith(self):
        self.assertEqual(self.manager.filter(TestModel.label.test(lifter.endswith('s'))),
                        [self.OBJECTS[1], self.OBJECTS[2]])

    def test_value_in(self):
        self.assertEqual(self.manager.filter(TestModel.label.test(lifter.value_in(['alabama', 'arkansas']))),
                        [self.OBJECTS[0], self.OBJECTS[1]])

    def test_range(self):
        self.assertEqual(self.manager.filter(TestModel.order.test(lifter.lookups.value_range(2, 3))),
                        [self.OBJECTS[0], self.OBJECTS[1]])

    def test_istartswith(self):
        self.assertEqual(self.manager.filter(TestModel.surname.test(lifter.istartswith('c'))),
                        [self.OBJECTS[1], self.OBJECTS[3]])

    def test_iendswith(self):
        self.assertEqual(self.manager.filter(TestModel.surname.test(lifter.iendswith('t'))),
                        [self.OBJECTS[0], self.OBJECTS[3]])

    def test_contains(self):
        self.assertEqual(self.manager.filter(TestModel.surname.test(lifter.contains('Lin'))),
                        [self.OBJECTS[2]])

    def test_icontains(self):
        self.assertEqual(self.manager.filter(TestModel.surname.test(lifter.icontains('lin'))),
                        [self.OBJECTS[2], self.OBJECTS[3]])

    def test_field_exists(self):

        families = [
            {
                'name': 'Community',
                'postal_adress': 'Greendale',
            },
            {
                'name': 'Misfits',
            }
        ]

        Family = lifter.models.Model('Family')
        manager = Family.load(families)

        self.assertEqual(manager.filter(Family.postal_adress.exists()), [families[0]])
        self.assertEqual(manager.filter(~Family.postal_adress.exists()), [families[1]])

def mean(values):
    return float(sum(values)) / len(values)

class TestAggregation(TestBase):
    def test_sum(self):
        self.assertEqual(self.manager.aggregate((TestModel.a, sum)), {'a__sum': 6})
        self.assertEqual(self.manager.aggregate(total=(TestModel.a, sum)), {'total': 6})

    def test_min(self):
        self.assertEqual(self.manager.aggregate((TestModel.a, min)), {'a__min': 1})

    def test_max(self):
        self.assertEqual(self.manager.aggregate((TestModel.a, max)), {'a__max': 2})

    def test_mean(self):
        self.assertEqual(self.manager.aggregate((TestModel.a, mean)), {'a__mean': 1.5})

    def test_flat(self):
        self.assertEqual(self.manager.aggregate((TestModel.a, mean), flat=True), [1.5])

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
