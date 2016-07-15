import itertools
import operator
from collections import Iterator
import random
from . import exceptions
from . import utils
from . import lookups

REPR_OUTPUT_SIZE = 10


class Path(object):

    class DoesNotExist(object):
        pass

    def __init__(self, path=None):
        self.path = path or []
        self._reversed = False # used for order by
        self._getters = []

    def __getattr__(self, part):
        return self.__class__(self.path + [part])

    __getitem__ = __getattr__

    def __str__(self):
        return '.'.join(self.path)

    def __repr__(self):
        return '<Path: {0}>'.format(self)

    def __eq__(self, other):
        return QueryNode(path=self, lookup=lookups.registry['eq'](other))

    def __ne__(self, other):
        return QueryNode(path=self, lookup=lookups.registry['ne'](other))

    def __gt__(self, other):
        return QueryNode(path=self, lookup=lookups.registry['gt'](other))

    def __ge__(self, other):
        return QueryNode(path=self, lookup=lookups.registry['gte'](other))

    def __lt__(self, other):
        return QueryNode(path=self, lookup=lookups.registry['lt'](other))

    def __le__(self, other):
        return QueryNode(path=self, lookup=lookups.registry['lte'](other))

    def __invert__(self):
        """For reverse order_by"""
        return Ordering(self, reverse=True)

    def test(self, func, *args, **kwargs):
        return QueryNode(path=self, lookup=lookups.registry['test'](func, *args, **kwargs))

    def exists(self):
        return QueryNode(path=self, lookup=lookups.registry['exists'](), path_kwargs={'soft_fail': True})


class Ordering(object):

    def __init__(self, path, reverse=False, random=False):
        self.path = path
        self.reverse = reverse
        self.random = random

class Aggregation(object):
    def __init__(self, path, func):
        self.path = path
        self.func = func

    def __call__(self, aggregate):
        self.aggregate = aggregate

        return self

    def __repr__(self):
        return 'Aggregation({})'.format(self.func)

    def aggregate(self, data):
        return self.func(data)


class BaseQueryNode(object):
    def __init__(self, *args, **kwargs):
        self.inverted = kwargs.pop('inverted', False)

    def __and__(self, other):
        return QueryNodeWrapper('AND', self, other)

    def __or__(self, other):
        return QueryNodeWrapper('OR', self, other)

    def __invert__(self):
        return self.clone(inverted=not self.inverted)

class QueryNodeWrapper(BaseQueryNode):
    def __init__(self, operator, *args, **kwargs):
        super(QueryNodeWrapper, self).__init__(**kwargs)
        self.operator = operator
        self.subqueries = args

    def __repr__(self):
        if self.inverted:
            inverted_repr = 'NOT '
        else:
            inverted_repr = ''
        return '<QueryNodeWrapper {0}{1} ({2})>'.format(inverted_repr, self.operator, self.operator.join([repr(self.subqueries)]))

    def __and__(self, other):
        if hasattr(other, 'operator'):
            return super(QueryNodeWrapper, self).__and__(other)
        return self.clone(subqueries=list(self.subqueries) + [other])

    def __or__(self, other):
        if hasattr(other, 'operator'):
            return super(QueryNodeWrapper, self).__or__(other)
        return self.clone(subqueries=list(self.subqueries) + [other])

    def clone(self, **kwargs):
        kwargs.setdefault('inverted', self.inverted)
        new_query = self.__class__(
            kwargs.get('operator', self.operator),
            *kwargs.get('subqueries', self.subqueries),
            **kwargs)
        return new_query

class QueryNode(BaseQueryNode):
    """An abstract way to represent query, that will be compiled to an actual query by the manager"""
    def __init__(self, path, lookup, path_kwargs={}, **kwargs):
        self.path_kwargs = path_kwargs
        super(QueryNode, self).__init__(**kwargs)
        self.path = path
        self.lookup = lookup

    def __repr__(self):
        return '<QueryNode {0} {1}>'.format(self.path, self.lookup)

    def clone(self, **kwargs):
        kwargs.setdefault('path', self.path)
        kwargs.setdefault('lookup', self.lookup)
        kwargs.setdefault('inverted', self.inverted)
        kwargs.setdefault('path_kwargs', self.path_kwargs)
        return self.__class__(**kwargs)


def lookup_to_path(lookup):
    path = Path()
    for part in lookup.replace('__', '.').split('.'):
        path = getattr(path, part)
    return path


class Window(object):
    """Used to help dealing with sliced querysets"""

    def __init__(self, index):
        if isinstance(index, slice):
            self.start = index.start
            self.stop = index.stop
            if not self.stop:
                raise ValueError('you must provide a stop when slicing a queryset')
        else:
            raise ValueError('Accessing a single element from a queryset is not supported')

    def as_slice(self):
        return slice(self.start, self.stop)

    @property
    def start_as_int(self):
        try:
            return int(self.start)
        except TypeError:
            return 0

    @property
    def size(self):
        return self.stop - self.start_as_int

class Query(object):
    """Will gather all query related data (queried field, ordering, distinct, etc.)
    and be passed to the manager"""
    def __init__(self, action, filters=None, window=None, orderings=[], **hints):
        self.filters = filters
        self.orderings = orderings
        self.action = action
        self.window = window
        self.hints = hints

    def clone(self, **kwargs):
        base_kwargs = {
            'orderings': self.orderings,
            'action': self.action,
        }
        if self.filters:
            base_kwargs['filters'] = self.filters.clone()
        base_kwargs.update(**self.hints)
        base_kwargs.update(**kwargs)

        return self.__class__(**base_kwargs)

class QuerySet(object):
    def __init__(self, manager, model, query=None, orderings=None, distinct=False):
        self.model = model
        self.manager = manager
        self._populated = False
        self._data = []

        self.orderings = orderings
        self.query = query or Query(action='select')

        self.distinct_results = distinct

    def __repr__(self):
        suffix = ''
        if len(self.data) > REPR_OUTPUT_SIZE:
            suffix = " ...(remaining elements truncated)..."
        return '<QuerySet {0}{1}>'.format(self.data[:REPR_OUTPUT_SIZE], suffix)


    @property
    def data(self):
        if self._populated:
            return self._data
        return self._fetch_all()

    def _fetch_all(self):
        iterator = self.iterator()
        self._data = [item for item in iterator]
        self._populated = True
        return self._data

    def iterator(self):
        return self.manager.execute(self.query)

    def __eq__(self, other):
        return self.data == other

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for value in self.data:
            yield value

    def __getitem__(self, index):
        query = self.query.clone(window=Window(index))
        return self._clone(query=query)

    def _clone(self, query=None, orderings=None, **kwargs):
        orderings = orderings or self.orderings
        distinct = kwargs.get('distinct', self.distinct_results)
        return self.__class__(self.manager, model=self.model, query=query)

    def all(self):
        return self._clone()

    def first(self):
        try:
            return self.data[0]
        except IndexError:
            return None

    def last(self):
        try:
            return self.data[-1]
        except IndexError:
            return None

    def build_filter(self, *args, **kwargs):
        if not args and not kwargs:
            raise ValueError('You need to provide at least a query or some keyword arguments')

        final_arg_query = None
        for arg in args:
            if not final_arg_query:
                final_arg_query = arg
                continue
            final_arg_query = final_arg_query & arg

        kwargs_query = self.build_filter_from_kwargs(**kwargs)
        if kwargs_query and final_arg_query:
            final_query = final_arg_query & kwargs_query
        elif kwargs_query:
            final_query = kwargs_query
        else:
            final_query = final_arg_query

        return final_query

    def build_filter_from_kwargs(self, **kwargs):
        """Convert django-s like lookup to SQLAlchemy ones"""
        query = None
        for path_to_convert, value in kwargs.items():

            path_parts = path_to_convert.split('__')
            lookup_class = None
            try:
                # We check if the path ends with something such as __gte, __lte...
                lookup_class = lookups.registry[path_parts[-1]]
                path_to_convert = '__'.join(path_parts[:-1])
            except KeyError:
                pass
            path = lookup_to_path(path_to_convert)

            if lookup_class:
                q = QueryNode(path, lookup=lookup_class(value))
            else:
                q = path == value

            if query:
                query = query & q
            else:
                query = q
        return query

    def _combine_query_filters(self, query):
        if self.query.filters:
            return query & self.query.filters
        return query

    def filter(self, *args, **kwargs):
        final_filter = self.build_filter(*args, **kwargs)
        query = self.query.clone(action='select', filters=self._combine_query_filters(final_filter))
        return self._clone(query=query)

    def exclude(self, *args, **kwargs):
        final_filter = ~self.build_filter(*args, **kwargs)
        query = self.query.clone(action='select', filters=self._combine_query_filters(final_filter))
        return self._clone(query=query)

    def count(self):
        new_query = self.query.clone(action='count')
        return self.manager.execute(new_query)

    def _parse_ordering(self, *paths):
        orderings = []

        for path in paths:
            if isinstance(path, Ordering):
                # probably explicit reverted ordering using ~Model.attribute
                orderings.append(path)
                continue

            reverse = False
            if isinstance(path, str):
                if path == '?':
                    orderings.append(Ordering(None, random=True))
                    continue
                reverse = path.startswith('-')
                if reverse:
                    path = path[1:]
                path = self.arg_to_path(path)
            orderings.append(Ordering(path, reverse))

        return orderings

    def get(self, *args, **kwargs):
        qs = self.filter(*args, **kwargs)
        new_query = qs.query.clone(action='select', force_single=True)
        return qs.manager.execute(new_query)

    def order_by(self, *orderings):
        parsed_orderings = self._parse_ordering(*orderings)
        new_query = self.query.clone(orderings=parsed_orderings)
        return self._clone(query=new_query)

    def arg_to_path(self, arg):
        path = arg
        if isinstance(arg, str):
            path = lookup_to_path(arg)
        return path

    def values(self, *args):
        if not args:
            raise ValueError('Empty values')

        paths = [self.arg_to_path(arg) for arg in args]
        query = self.query.clone(action='values', paths=paths, mode='mapping')
        return self.manager.execute(query)

    def values_list(self, *args, **kwargs):
        if not args:
            raise ValueError('Empty values')

        paths = [self.arg_to_path(arg) for arg in args]

        if kwargs.get('flat', False) and len(paths) > 1:
            raise ValueError('You cannot set flat to True if you want to return multiple values')

        query = self.query.clone(action='values', paths=paths, mode='iterable', flat=kwargs.get('flat'))
        return self.manager.execute(query)

    def _get_aggregate_key(self, aggregation, function_name, key=None):
        if key:
            final_key = key
        else:
            func_name = function_name or aggregation.func.__name__ if aggregation.func.__name__ != '<lambda>' else key
            final_key = '{0}__{1}'.format(str(aggregation.path), func_name)
        return final_key

    def aggregate(self, *args, **kwargs):
        data = {}  # Isn't lazy
        flat = kwargs.pop('flat', False)

        aggregates = []
        for conf in args:
            function_name = None
            try:
                # path / function tuple aggregate
                path, func = conf
            except TypeError:
                # Django-like aggregate
                path = lookup_to_path(conf.attr_name)
                func = conf.aggregate
                function_name = conf.name

            aggregation = Aggregation(path, func)
            aggregates.append(
                (
                    self._get_aggregate_key(aggregation, function_name),
                    aggregation
                )
            )

        for key, conf in kwargs.items():
            function_name = None
            try:
                # path / function tuple aggregate
                path, func = conf
            except TypeError:
                # Django-like aggregate
                path = lookup_to_path(conf.attr_name)
                func = conf.aggregate
                function_name = conf.name

            aggregation = Aggregation(path, func)
            aggregates.append(
                (
                    self._get_aggregate_key(aggregation, function_name, key),
                    aggregation
                )
            )

        query = self.query.clone(action='aggregate', aggregates=aggregates, flat=flat)
        return self.manager.execute(query)

    def distinct(self):
        new_query = self.query.clone(distinct=True)
        return self._clone(query=new_query)

    def exists(self, from_backend=False):
        if from_backend:
            new_query = self.query.clone(action='exists')
            return self.manager.execute(new_query)
        return len(self) > 0

    def locally(self):
        """
        Will execute the current queryset and pass it to the python backend
        so user can run query on the local dataset (instead of contacting the store)
        """

        from .backends import python
        from . import models

        store = python.IterableStore(values=self)
        return store.query(self.manager.model).all()
