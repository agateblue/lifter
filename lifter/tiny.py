import itertools
from collections import Iterator
from random import sample
from lifter import utils, DoesNotExist, MultipleObjectsReturned


class Order(object):
    ASC = 1
    DESC = 2


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

    def test(self, func):
        return self._query.test(func)

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
        self.test = test
        self.hashval = hashval

    def __repr__(self):
        template = 'QueryImpl({0} {1})' if len(self.hashval) == 2 else 'QueryImpl({1} {0} {2})'

        return template.format(*self.hashval)

    def __call__(self, val):
        return self.test(val)

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

    def _generate_test(self, test, hashval):
        def impl(value):
            return test(self.path.get(value))

        return QueryImpl(impl, hashval)

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


    # __contains__, matches, search, any, all, exists probably


class TinyQuerySet(object):
    def __init__(self, data):
        if isinstance(data, Iterator):
            self._iter_data = data
            self._data = []
        else:
            self._iter_data = None
            self._data = data


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

    def get(self, query):
        matches = list(filter(query, iter(self.data)))
        if len(matches) == 0:
            raise DoesNotExist()
        if len(matches) > 1:
            raise MultipleObjectsReturned()
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

    def filter(self, query):
        return self._clone(filter(query, self.data))

    def exclude(self, query):
        return self._clone(filter(lambda val: not query(val), self.data))

    def count(self):
        return len(list(self.data))

    def order_by(self, path, reverse=False):
        if isinstance(path, str) and path == '?':
            # Random ordering
            return self._clone(sample(self.data, len(self.data)))

        def create_generator():
            return sorted(self.data, key=path.get, reverse=reverse) # sorted is not lazy

        return self._clone(create_generator())

    def values(self, *args):
        return self._clone(  # I believe in this case we should return raw data not query_set
            map(
                lambda val: {str(path):path.get(val) for path in args},
                self.data
            )
        )

    def values_list(self, *args, **kwargs):  # "*args, flat=False" is Python 3.5 specific, will use **kwargs in older versions
        if not args:
            raise ValueError('Empty values')

        getter = lambda val: tuple(path.get(val) for path in args)

        if kwargs.get('flat', False) and len(args) > 1:
            raise ValueError('You cannot set flat to True if you want to return multiple values')
        elif kwargs.get('flat', False):
            getter = lambda val: args[0].get(val)

        return self._clone(  # I believe in this case we should return raw data not query_set
            map(getter, self.data)
        )

    def _build_aggregate(self, aggregation, key=None):
        if key:
            final_key = key
        else:
            func_name = aggregation.func.__name__ if aggregation.func.__name__ != '<lambda>' else key
            final_key = '{0}__{1}'.format(str(aggregation.path), func_name)
        values = (aggregation.path.get(val) for val in self.data)
        return aggregation.aggregate(values), final_key

    def aggregate(self, *args, **kwargs):
        data = {}  # Isn't lazy
        flat = kwargs.pop('flat', False)

        for path, func in args:
            aggregation = Aggregation(path, func)
            aggregate, key = self._build_aggregate(aggregation)
            data[key] = aggregate
        for key, conf in kwargs.items():
            path, func = conf
            aggregation = Aggregation(path, func)
            aggregate, key = self._build_aggregate(aggregation, key)
            data[key] = aggregate


        if flat:
            return list(data.values())  # Isn't lazy

        return data

    def distinct(self):
        return self._clone(utils.unique_everseen(self.data))

    def exists(self):
        return len(self) > 0

class BaseModelMeta(type):
    def __getattr__(cls, key):
        return getattr(p, key)

class BaseModel(object):
    __metaclass__ = BaseModelMeta

    @classmethod
    def load(cls, values):
        return TinyQuerySet(values)

def Model(name):
    return BaseModelMeta(name, (BaseModel,), {})


# q = Query()  # filter, exclude, get
p = Path()  # order_by, values, values_list
# a = Aggregation()  # aggregate
