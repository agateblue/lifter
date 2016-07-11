import operator

from . import base
from .. import query
from .. import store
from .. import exceptions
from .. import utils
from .. import managers


class PythonPath(query.Path):

    def get(self, data, **kwargs):
        if not self._getters:
            # Since this is one of the most called method in lifter, we avoid
            # any call to other methods here
            for part in self.path:
                self._getters.append(utils.attrgetter(part))

        try:
            for getter in self._getters:
                data = getter(data)
        except exceptions.MissingAttribute:
            if kwargs.get('soft_fail', False):
                return query.Path.DoesNotExist
            raise
        return data

class PythonModel(base.BaseModel):
    __metaclass__ = base.BaseModelMeta
    path_class = PythonPath

    @classmethod
    def load(cls, iterable, **kwargs):
        return PythonManager(store=iterable, model=cls, **kwargs)

def get_wrapper(query):
    inverted = query.inverted
    subqueries = [QueryImpl(subquery) for subquery in query.subqueries]

    if query.operator == 'AND':
        matcher = all
    else:
        matcher = any

    def wrapper(obj):
        result =  matcher((q(obj) for q in subqueries))
        if inverted:
            return not result
        return result
    return wrapper

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
            path_kwargs = self.base_query.path_kwargs
            def leaf_query(obj):
                value = self.base_query.path.get(obj, **path_kwargs)
                result = test(value, *args, **kwargs)
                if inverted:
                    return not result
                return result
            return leaf_query

    def __call__(self, obj):
        return self.test(obj)


class IterableStore(store.Store):

    def __init__(self, values):
        self.values = values

    def get_all_values(self, query):
        return self.values

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
                iterator = sorted(iterator, key=ordering.path.get, reverse=ordering.reverse)

        if query.hints.get('distinct', False):
            iterator = utils.unique_everseen(iterator)
        return iterator

    def handle_values(self, query):
        data = self.handle_select(query)
        if query.hints['mode'] == 'mapping':
            getter = lambda val: {str(path):path.get(val) for path in query.hints['paths']}
        else:
            if query.hints.get('flat', False):
                getter = lambda val: query.hints['paths'][0].get(val)
            else:
                getter = lambda val: tuple(path.get(val) for path in query.hints['paths'])
        return PythonModel.load(map(getter, data)).all()


class PythonManager(managers.Manager):

    def match(self, query, obj):
        compiled_query = QueryImpl(query)
        return compiled_query(obj)

    def __init__(self, *args, **kwargs):
        store = kwargs.get('store')
        if not hasattr(store, 'get_all_values'):
            kwargs['store'] = IterableStore(store)

        super(PythonManager, self).__init__(*args, **kwargs)
