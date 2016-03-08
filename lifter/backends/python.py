import operator

from . import base
from .. import query
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
    def load(cls, values):
        return PythonManager(values=values, model=cls)

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


class PythonManager(managers.Manager):

    def __init__(self, *args, **kwargs):
        self._values = kwargs.pop('values')
        super(PythonManager, self).__init__(*args, **kwargs)

    def get(self, query, orderings, **kwargs):
        iterator = self.execute_query(query, orderings=None)
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


    def _raw_data_iterator(self, compiled_query):
        if not compiled_query:
            for obj in self._values:
                yield obj
        else:
            for obj in self._values:
                if compiled_query(obj):
                    yield obj
        # return filter(self.query, self._iter_data)

    def match(self, query, obj):
        compiled_query =  QueryImpl(query)
        return compiled_query(obj)

    def execute_query(self, query, orderings, **kwargs):
        compiled_query = None
        if query:
            compiled_query =  QueryImpl(query)

        iterator = self._raw_data_iterator(compiled_query)

        if orderings:
            random_value = lambda v: random.random()

            for ordering in reversed(orderings):
                # We loop in reverse order because we found no other way to handle multiple sorting
                # in different directions right now

                if ordering.random:
                    iterator = sorted(iterator, key=random_value)
                    continue
                iterator = sorted(iterator, key=ordering.path.get, reverse=ordering.reverse)

        if kwargs.get('distinct', False):
            iterator = utils.unique_everseen(iterator)
        return iterator

    def values_list(self, paths, *args, **kwargs):
        data = self.execute_query(kwargs['query'], kwargs['orderings'])
        if kwargs.get('flat', False):
            getter = lambda val: paths[0].get(val)
        else:
            getter = lambda val: tuple(path.get(val) for path in paths)

        return PythonModel.load(map(getter, data)).all()

    def values(self, paths, *args, **kwargs):
        data = self.execute_query(kwargs['query'], kwargs['orderings'])
        return PythonModel.load(map(
                lambda val: {str(path):path.get(val) for path in paths},
                data
            )
        ).all()
