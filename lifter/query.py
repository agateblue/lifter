import itertools
from collections import Iterator
import random
from . import exceptions
from . import utils

REPR_OUTPUT_SIZE = 10


def filter_values(func, values):
    """We implement a lazy filter since built-in filter() is not lazy in Python2"""
    for value in values:
        if func(value):
            yield value

class Path(object):
    def __init__(self, path=None):
        self.path = path or []
        self._reversed = False # used for order by

    def __getattr__(self, part):
        return self.__class__(self.path + [part])

    __getitem__ = __getattr__

    def __str__(self):
        return '.'.join(self.path)

    def get(self, data):
        for part in self.path:
            getter = utils.attrgetter(part)
            data = getter(data)

        return data

    @property
    def _query(self):
        return Query(self)

    def __eq__(self, other):
        return self._query.__eq__(other)

    def __ne__(self, other):
        return self._query.__ne__(other)

    def __gt__(self, other):
        return self._query.__gt__(other)

    def __ge__(self, other):
        return self._query.__ge__(other)

    def __lt__(self, other):
        return self._query.__lt__(other)

    def __le__(self, other):
        return self._query.__le__(other)

    def __invert__(self):
        """For reverse order_by"""
        return Ordering(self, reverse=True)

    def test(self, func):
        return self._query.test(func)

    def exists(self):
        return self._query.exists()

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


class QueryImpl(object):
    def __init__(self, test, hashval):
        self._test = test
        self.hashval = hashval

    def match(self, val):
        return self._test(val)

    def __repr__(self):
        template = 'QueryImpl({0} {1})' if len(self.hashval) == 2 else 'QueryImpl({1} {0} {2})'

        return template.format(*self.hashval)

    def __call__(self, val):
        return self.match(val)

    def __and__(self, other):
        return QueryImpl(
            lambda val: self(val) and other(val),
            ('&', self, other)
        )

    def __or__(self, other):
        return QueryImpl(
            lambda val: self(val) or other(val),
            ('|', self, other)
        )

    def __invert__(self):
        return QueryImpl(
            lambda val: not self(val),
            ('not', self, '')
        )


class Query(object):
    def __init__(self, path):
        self.path = path

    def _get_impl(self, test, **kwargs):
        def impl(obj):
            value = self.path.get(obj)
            if isinstance(value, utils.IterableAttr):
                return value._resolve_test(test, **kwargs)
            return test(value)
        return impl

    def _generate_test(self, test, hashval):

        return QueryImpl(self._get_impl(test), hashval)

    def __call__(self, callable):
        raise NotImplementedError()

    def __eq__(self, other):
        return self._generate_test(
            lambda val: val == other, ('==', self.path, other)
        )

    def __ne__(self, other):
        return self._generate_test(
            lambda val: val != other, ('!=', self.path, other)
        )

    def __gt__(self, other):
        return self._generate_test(
            lambda val: val > other, ('>', self.path, other)
        )

    def __ge__(self, other):
        return self._generate_test(
            lambda val: val >= other, ('>=', self.path, other)
        )

    def __lt__(self, other):
        return self._generate_test(
            lambda val: val < other, ('<', self.path, other)
        )

    def __le__(self, other):
        return self._generate_test(
            lambda val: val <= other, ('<=', self.path, other)
        )

    def test(self, func):
        return self._generate_test(
            func, ('test', self.path, func)
        )

    def exists(self):
        def _base_impl(obj):
            return True

        base_impl = self._get_impl(lambda obj: True, fail_silently=True)

        def impl(obj):
            try:
                return base_impl(obj)
            except exceptions.MissingAttribute:
                return False

        return QueryImpl(impl, ('exists', self.path))

    # __contains__, matches, search, any, all, exists probably

def lookup_to_path(lookup):
    path = Path()
    for part in lookup.replace('__', '.').split('.'):
        path = getattr(path, part)
    return path

class QuerySet(object):
    def __init__(self, data):
        self._populated = False
        if isinstance(data, Iterator):
            self._iter_data = data
            self._data = []
        else:
            self._iter_data = None
            self._data = data
            self._populated = True
    def __repr__(self):
        suffix = ''
        if len(self.data) > REPR_OUTPUT_SIZE:
            suffix = " ...(remaining elements truncated)..."
        return '<QuerySet {0}{1}>'.format(self.data[:REPR_OUTPUT_SIZE], suffix)

    @property
    def __data(self):  # pretty ugly
        if self._iter_data:
            for val in self._iter_data:
                self._data.append(val)

                yield val

        self._iter_data = None

    @property
    def data(self):
        if self._data:
            return self._data
        return self._fetch_all()

    def _fetch_all(self):
        self._data = [item for item in self.iterator()]
        self._populated = True
        return self._data

    def iterator(self):
        return itertools.chain(self._data, self.__data)

    def __eq__(self, other):
        return self.data == other

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for value in self.data:
            yield value

    def __getitem__(self, index):
        return self.data[index]

    def _clone(self, new_values):
        return self.__class__(new_values)

    def all(self):
        return self._clone(self.data)

    def get(self, *args, **kwargs):
        final_query = self.build_query(*args, **kwargs)
        matches = list(filter_values(final_query, iter(self.data)))
        if len(matches) == 0:
            raise exceptions.DoesNotExist()
        if len(matches) > 1:
            raise exceptions.MultipleObjectsReturned()
        return matches[0]

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

    def build_query(self, *args, **kwargs):
        if not args and not kwargs:
            raise ValueError('You need to provide at least a query or some keyword arguments')

        final_arg_query = None
        for arg in args:
            if not final_arg_query:
                final_arg_query = arg
                continue
            final_arg_query = final_arg_query & arg

        kwargs_query = self.build_query_from_kwargs(**kwargs)
        if kwargs_query and final_arg_query:
            final_query = final_arg_query & kwargs_query
        elif kwargs_query:
            final_query = kwargs_query
        else:
            final_query = final_arg_query

        return final_query

    def build_query_from_kwargs(self, **kwargs):
        """Convert django-s like lookup to SQLAlchemy ones"""
        query = None
        for lookup, value in kwargs.items():
            path = lookup_to_path(lookup)

            if hasattr(value, '__call__'):
                q = path.test(value)
            else:
                q = path == value

            if query:
                query = query & q
            else:
                query = q
        return query

    def filter(self, *args, **kwargs):
        final_query = self.build_query(*args, **kwargs)

        return self._clone(filter_values(final_query, self.data))

    def exclude(self, *args, **kwargs):
        final_query = self.build_query(*args, **kwargs)

        return self._clone(filter_values(lambda val: not final_query(val), self.data))

    def count(self):
        return len(self.data)

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

    def order_by(self, *orderings):
        parsed_orderings = self._parse_ordering(*orderings)
        # ordering = parsed_orderings[0]

        random_value = lambda v: random.random()

        sorter = self.iterator()
        for ordering in reversed(parsed_orderings):
            # We loop in reverse order because we found no other way to handle multiple sorting
            # in different directions right now

            if ordering.random:
                sorter = sorted(sorter, key=random_value)
                continue
            sorter = sorted(sorter, key=ordering.path.get, reverse=ordering.reverse)
        # print(sorter)
        # def create_generator():
        #     return sorted(self.iterator(), key=ordering.path.get, reverse=ordering.reverse) # sorted is not lazy

        return self._clone(sorter)

    def arg_to_path(self, arg):
        path = arg
        if isinstance(arg, str):
            path = lookup_to_path(arg)
        return path

    def _value_resolver(self, path):
        def getter(obj):
            value = path.get(obj)
            if isinstance(value, utils.IterableAttr):
                return value.get_resolved_items()
            return value
        return getter

    def values(self, *args):
        if not args:
            raise ValueError('Empty values')

        final_paths = [self.arg_to_path(arg) for arg in args]

        return self._clone(  # I believe in this case we should return raw data not query_set
            map(
                lambda val: {str(path):self._value_resolver(path)(val) for path in final_paths},
                self.data
            )
        )

    def values_list(self, *args, **kwargs):
        if not args:
            raise ValueError('Empty values')

        final_paths = [self.arg_to_path(arg) for arg in args]

        getter = lambda val: tuple(self._value_resolver(path)(val) for path in final_paths)

        if kwargs.get('flat', False) and len(final_paths) > 1:
            raise ValueError('You cannot set flat to True if you want to return multiple values')
        elif kwargs.get('flat', False):
            getter = lambda val: self._value_resolver(final_paths[0])(val)

        return self._clone(  # I believe in this case we should return raw data not query_set
            map(getter, self.data)
        )

    def _build_aggregate(self, aggregation, function_name=None, key=None):
        if key:
            final_key = key
        else:
            func_name = function_name or aggregation.func.__name__ if aggregation.func.__name__ != '<lambda>' else key
            final_key = '{0}__{1}'.format(str(aggregation.path), func_name)
        values = list((aggregation.path.get(val) for val in self.data))
        return aggregation.aggregate(values), final_key

    def aggregate(self, *args, **kwargs):
        data = {}  # Isn't lazy
        flat = kwargs.pop('flat', False)

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
            aggregate, key = self._build_aggregate(aggregation, function_name=function_name)
            data[key] = aggregate
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
            aggregate, key = self._build_aggregate(aggregation, function_name=function_name, key=key)
            data[key] = aggregate


        if flat:
            return list(data.values())  # Isn't lazy

        return data

    def distinct(self):
        return self._clone(utils.unique_everseen(self.data))

    def exists(self):
        return len(self) > 0
