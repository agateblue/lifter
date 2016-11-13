import unittest

from lifter import query, models
from lifter import aggregates
from lifter.backends.python import IterableStore


class TModel(models.Model):
    pass



class TestQuery(unittest.TestCase):

    def test_path_is_hashable(self):
        p1 = TModel.order
        p2 = TModel.order
        self.assertEqual(hash(p1), hash(p2))

    def test_ordering_is_hashable(self):
        o1 = query.Ordering(TModel.order, reverse=True)
        o2 = query.Ordering(TModel.order, reverse=True)

        self.assertEqual(hash(o1), hash(o2))

    def test_aggregation_is_hashable(self):
        a1 = aggregates.Aggregate('test')
        a2 = aggregates.Aggregate('test')

        self.assertEqual(hash(a1), hash(a2))

    def test_one_value_lookup_is_hashable(self):
        a1 = (TModel.order > 1).lookup
        a2 = (TModel.order > 1).lookup

        self.assertEqual(hash(a1), hash(a2))

    def test_query_node_is_hashable(self):
        a1 = (TModel.order > 1)
        a2 = (TModel.order > 1)

        self.assertEqual(hash(a1), hash(a2))

    def test_query_node_wrapper_is_hashable(self):
        a1 = (TModel.order > 1) & (TModel.order < 12)
        a2 = (TModel.order > 1) & (TModel.order < 12)

        self.assertEqual(hash(a1), hash(a2))

    def test_window_is_hashable(self):
        a1 = query.Window(slice(1, 2))
        a2 = query.Window(slice(1, 2))

        self.assertEqual(hash(a1), hash(a2))

    def test_query_is_hashable(self):
        store = IterableStore([])
        manager = store.query(TModel)
        qs = manager.filter((TModel.order > 1) & (TModel.order < 12))
        qs = qs.order_by(TModel.a, ~TModel.order)

        query = qs.query
        query.hints['aggregates'] = (aggregates.Sum('value'),)
        a1 = query
        a2 = a1.clone()

        self.assertEqual(hash(a1), hash(a2))
