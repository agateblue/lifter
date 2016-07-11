import operator

from . import base
from .. import query
from .. import models
from .. import store
from .. import exceptions
from .. import utils
from .. import managers


def get_wrapper(query):
    inverted = query.inverted
    subqueries = [QueryImpl(subquery) for subquery in query.subqueries]

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


def path_to_value(data, path, **kwargs):
    soft_fail = kwargs.pop('soft_fail', False)
    getters = [utils.attrgetter(part) for part in path.path]

    try:
        for getter in getters:
            data = getter(data)
    except exceptions.MissingAttribute:
        if soft_fail:
            return query.Path.DoesNotExist
        raise
    return data


class QueryImpl(object):
    def __init__(self, base_query):
        self.base_query = base_query
        self.test = self.setup_test()

    def setup_test(self):
        try:
            # query wrapper
            return get_wrapper(self.base_query)
        except AttributeError:
            # Leaf query
            test = self.base_query.test
            args, kwargs = self.base_query.test_args, self.base_query.test_kwargs
            inverted = self.base_query.inverted
            def leaf_query(obj):
                value = path_to_value(obj, self.base_query.path, **self.base_query.path_kwargs)
                result = test(value, *args, **kwargs)
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

    def __init__(self, *args, **kwargs):
        store = kwargs.get('store')
        if not hasattr(store, 'get_all_values'):
            kwargs['store'] = IterableStore(store)

        super(PythonManager, self).__init__(*args, **kwargs)

class RefinedIterableStore(store.RefinedStore):

    manager_class = PythonManager

    def get_all_values(self, query):
        return self.parent.values

    def get_values(self, query):
        compiled_filters = None
        if query.filters:
            compiled_filters = QueryImpl(query.filters)

        if not compiled_filters:
            for obj in self.get_all_values(query):
                yield obj
        else:
            for obj in self.get_all_values(query):
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

    def handle_exists(self, query):
        iterator = self.handle_select(query.clone(orderings=None))
        for row in iterator:
            return True
        return False

    def handle_count(self, query):
        return len(list(self.handle_select(query.clone(orderings=None))))

    def handle_select(self, query):

        iterator = self.get_values(query)

        if query.hints.get('force_single', False):
            return self.select_single(iterator)
        if query.orderings:
            random_value = lambda v: random.random()

            for ordering in reversed(query.orderings):
                # We loop in reverse order because we found no other way to handle multiple sorting
                # in different directions right now

                if ordering.random:
                    iterator = sorted(iterator, key=random_value)
                    continue
                l = lambda v: path_to_value(v, ordering.path)
                iterator = sorted(iterator, key=l, reverse=ordering.reverse)

        if query.hints.get('distinct', False):
            iterator = utils.unique_everseen(iterator)
        return iterator

    def handle_values(self, query):
        data = self.handle_select(query)
        if query.hints['mode'] == 'mapping':
            getter = lambda val: {str(path):path_to_value(val, path) for path in query.hints['paths']}
        else:
            if query.hints.get('flat', False):
                getter = lambda val: path_to_value(val, query.hints['paths'][0])
            else:
                getter = lambda val: tuple(path_to_value(val, path) for path in query.hints['paths'])
        values = map(getter, data)

        return IterableStore(values).query(models.Model).all()

    def collect_values(self, data, aggregates):
        r = {}
        for row in data:
            for key, aggregate in aggregates:
                l = r.setdefault(key, [])
                l.append(path_to_value(row, aggregate.path))
        return r

    def handle_aggregate(self, query):
        data = self.handle_select(query)
        values = self.collect_values(data, query.hints['aggregates'])
        print(values)
        if query.hints.get('flat', False):
            return [
                aggregate.aggregate(values[key])
                for key, aggregate in query.hints['aggregates']
            ]
        return {
            key: aggregate.aggregate(values[key])
            for key, aggregate in query.hints['aggregates']
        }


class IterableStore(store.Store):

    refined_class = RefinedIterableStore

    def __init__(self, values):
        self.values = values
