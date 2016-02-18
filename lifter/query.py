# -*- coding: utf-8 -*-

from collections import OrderedDict

from . import utils


REPR_OUTPUT_SIZE = 10


class DoesNotExist(ValueError):
    pass


class MultipleObjectsReturned(ValueError):
    pass


class QuerySet(object):
    def __init__(self, values):
        self._values = list(values)

    def __iter__(self):
        for value in self._values:
            yield value
        raise StopIteration

    def __len__(self):
        return len(self._values)

    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, str(list(self._values)))

    def __getitem__(self, i):
        return self._values[i]

    def __eq__(self, other):
        return self._values == list(other)

    def _clone(self, new_values):
        return self.__class__(new_values)

    def __repr__(self):
        data = list(self[:REPR_OUTPUT_SIZE + 1])
        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."
        return '<QuerySet %r>' % data

    def _build_filter(self, **kwargs):
        """build a single filter function used to match arbitrary object"""

        def object_filter(obj):
            for key, value in kwargs.items():
                # we replace dango-like lookup by dots, so attrgetter can do his job

                getter = utils.attrgetter(key)
                if hasattr(value, '__call__'):
                    # User passed a callable for a custom comparison
                    if not value(getter(obj)):
                        return False
                else:
                    if not getter(obj) == value:
                        return False
            return True

        return object_filter

    def exists(self):
        return len(self) > 0

    def order_by(self, key):
        reverse = False
        if key.startswith('-'):
            reverse = True
            key = key[1:]

        return self._clone(sorted(self._values, key=utils.attrgetter(key), reverse=reverse))

    def all(self):
        return self._clone(self._values)

    def count(self):
        return len(self)

    def first(self):
        try:
            return self._values[0]
        except IndexError:
            return None

    def last(self):
        try:
            return self._values[-1]
        except IndexError:
            return None

    def filter(self, **kwargs):
        _filter = self._build_filter(**kwargs)
        return self._clone(filter(_filter, self._values))

    def exclude(self, **kwargs):
        _filter = self._build_filter(**kwargs)
        return self._clone(filter(lambda v: not _filter(v), self._values))

    def get(self, **kwargs):

        matches = self.filter(**kwargs)
        if len(matches) == 0:
            raise DoesNotExist()
        if len(matches) > 1:
            raise MultipleObjectsReturned()
        return matches[0]

    def aggregate(self, *args, **kwargs):
        data = {}
        flat = kwargs.pop('flat', False)
        for aggregate in args:
            data[aggregate.identifier] = aggregate.aggregate(self._values)
        for key, aggregate in kwargs.items():
            data[key] = aggregate.aggregate(self._values)
        if flat:
            data = data.values()
        return data

    def values(self, *args):
        def getter(obj):
            data = {}
            for arg in args:
                g = utils.attrgetter(arg)
                data[arg] = g(obj)
            return data
        all_values = [getter(obj) for obj in self._values]
        return self._clone(all_values)

    def values_list(self, *args, **kwargs):
        flat = kwargs.get('flat', False)
        if flat and len(args) > 1:
            raise ValueError('You cannot set flat to True if you want to return multiple values')

        def getter(obj):
            if flat:
                return utils.attrgetter(args[0])(obj)
            return tuple((utils.attrgetter(arg)(obj) for arg in args))

        all_values = list([getter(obj) for obj in self._values])
        return self._clone(all_values)

    def distinct(self):
        return self._clone(utils.unique_everseen(self._values))

class Manager(object):
    """Used to retrieve / order / filter preferences pretty much as django's ORM managers"""

    def __init__(self, values, queryset_class=QuerySet):
        self._values = values
        self.queryset_class = queryset_class

    def get_queryset(self):
        return self.queryset_class(self._values)

    def all(self):
        return self.get_queryset().all()

    def __getattr__(self, attr):
        try:
            return super(Manager, self).__getattr__(attr)
        except AttributeError:
            # Try to proxy on queryset if possible
            return getattr(self.get_queryset(), attr)
