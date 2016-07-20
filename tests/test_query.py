import unittest

from lifter import query, models
from lifter import aggregates
from lifter.backends.python import IterableStore


class TestModel(models.Model):
    pass



class TestQuery(unittest.TestCase):

    def test_path_is_hashable(self):
        p1 = TestModel.order
        p2 = TestModel.order
        self.assertEqual(hash(p1), hash(p2))

    def test_ordering_is_hashable(self):
        o1 = query.Ordering(TestModel.order, reverse=True)
        o2 = query.Ordering(TestModel.order, reverse=True)

        self.assertEqual(hash(o1), hash(o2))

    def test_aggregation_is_hashable(self):
        a1 = aggregates.Aggregate('test')
        a2 = aggregates.Aggregate('test')

        self.assertEqual(hash(a1), hash(a2))

    def test_one_value_lookup_is_hashable(self):
        a1 = (TestModel.order > 1).lookup
        a2 = (TestModel.order > 1).lookup

        self.assertEqual(hash(a1), hash(a2))

    def test_query_node_is_hashable(self):
        a1 = (TestModel.order > 1)
        a2 = (TestModel.order > 1)

        self.assertEqual(hash(a1), hash(a2))

    def test_query_node_wrapper_is_hashable(self):
        a1 = (TestModel.order > 1) & (TestModel.order < 12)
        a2 = (TestModel.order > 1) & (TestModel.order < 12)

        self.assertEqual(hash(a1), hash(a2))

    def test_window_is_hashable(self):
        a1 = query.Window(slice(1, 2))
        a2 = query.Window(slice(1, 2))

        self.assertEqual(hash(a1), hash(a2))

    def test_query_is_hashable(self):
        store = IterableStore([])
        manager = store.query(TestModel)
        qs = manager.filter((TestModel.order > 1) & (TestModel.order < 12))
        qs = qs.order_by(TestModel.a, ~TestModel.order)

        query = qs.query
        query.hints['aggregates'] = (aggregates.Sum('value'),)
        a1 = query
        a2 = a1.clone()

        self.assertEqual(hash(a1), hash(a2))
