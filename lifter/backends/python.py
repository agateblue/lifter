import operator

from . import base
from .. import query
from .. import models
from .. import store
from .. import exceptions
from .. import lookups
from .. import utils
from .. import managers


def get_wrapper(query, hints):
    inverted = query.inverted
    subqueries = [
        QueryImpl(subquery, hints=hints)
        for subquery in query.subqueries]

    if query.operator == 'AND':
        matcher = all
    else:
        matcher = any

    def wrapper(obj):
        result = matcher((q(obj) for q in subqueries))
        if inverted:
            return not result
        return result
    return wrapper


class QueryImpl(object):

    def __init__(self, base_query, hints):
        self.base_query = base_query
        self.hints = hints
        self.test = self.setup_test()

    def setup_test(self):
        try:
            # query wrapper
            return get_wrapper(self.base_query, hints=self.hints)
        except AttributeError:
            # Leaf query
            lookup = self.base_query.lookup
            inverted = self.base_query.inverted
            soft_fail = self.hints.get(
                'permissive',
                self.base_query.path_kwargs.get('soft_fail', False))
            def leaf_query(obj):
                value = store.path_to_value(obj, self.base_query.path, soft_fail=soft_fail)
                result = lookup.lookup(value)
                if inverted:
                    return not result
                return result
            return leaf_query

    def __call__(self, obj):
        return self.test(obj)


class PythonManager(managers.Manager):

    def match(self, query, obj):
        compiled_query = QueryImpl(query)
        return compiled_query(obj)


class IterableStore(store.Store):
    manager_class = PythonManager

    def __init__(self, values, *args, **kwargs):
        self.values = values
        super(IterableStore, self).__init__(*args, **kwargs)

    def get_default_adapter(self, model):
        return None


    def get_values(self, query):
        compiled_filters = None
        if query.filters:
            compiled_filters = QueryImpl(query.filters, hints=query.hints)

        if not compiled_filters:
            for obj in self.values:
                yield obj
        else:
            for obj in self.values:
                if compiled_filters(obj):
                    yield obj
        # return filter(self.query, self._iter_data)

    def select_single(self, iterator):
        first_match = None
        for match in iterator:
            # Little hack to avoid looping over the whole results set
            if not first_match:
                first_match = match
                continue
            raise exceptions.MultipleObjectsReturned()

        if not first_match:
            raise exceptions.DoesNotExist()

        return first_match

    def handle_exists(self, query, model):
        iterator = self.handle_select(query.clone(orderings=None), model)
        for row in iterator:
            return True
        return False

    def handle_count(self, query, model):
        return len(list(self.handle_select(query.clone(orderings=None), model)))

    def handle_select(self, query, model):

        iterator = self.get_values(query)

        if query.hints.get('force_single', False):
            return [self.select_single(iterator)]
        if query.orderings:
            random_value = lambda v: random.random()

            for ordering in reversed(query.orderings):
                # We loop in reverse order because we found no other way to handle multiple sorting
                # in different directions right now

                if ordering.random:
                    iterator = sorted(iterator, key=random_value)
                    continue
                l = lambda v: store.path_to_value(v, ordering.path)
                iterator = sorted(iterator, key=l, reverse=ordering.reverse)

        if query.hints.get('distinct', False):
            iterator = utils.unique_everseen(iterator)
        if query.window:
            return list(iterator)[query.window.as_slice()]
        return iterator

    def handle_values(self, query, model):
        return self.handle_select(query, model)

    def collect_values(self, data, aggregates):
        r = {}
        for row in data:
            for key, aggregate in aggregates:
                l = r.setdefault(key, [])
                l.append(store.path_to_value(row, aggregate.path))
        return r

    def handle_aggregate(self, query, model):
        data = self.handle_select(query, model)
        values = self.collect_values(data, query.hints['aggregates'])
        if query.hints.get('flat', False):
            return [
                aggregate.aggregate(values[key])
                for key, aggregate in query.hints['aggregates']
            ]
        return {
            key: aggregate.aggregate(values[key])
            for key, aggregate in query.hints['aggregates']
        }


class DummyStore(store.Store):
    """
    A dummy store that cannot understand / execute queries but instead
    will cast results from source to model, then hand over the model instances
    to an IterableStore
    """

    def load(self, model, adapter):
        raise NotImplementedError

    def _execute(self, query, model, adapter, raw=False):
        """
        We have to override this because in some situation
        (such as with Filebackend, or any dummy backend)
        we have to parse / adapt results *before* when can execute the query
        """
        values = self.load(model, adapter)
        return IterableStore(values=values)._execute(query, model=model, adapter=None, raw=raw)
