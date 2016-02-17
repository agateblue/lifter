# -*- coding: utf-8 -*-

import operator


def attrgetter(*items):

    if any(not isinstance(item, str) for item in items):
        raise TypeError('attribute name must be a string')
    if len(items) == 1:
        attr = items[0]
        def g(obj):
            return resolve_attr(obj, attr)
    else:
        def g(obj):
            return tuple(resolve_attr(obj, attr) for attr in items)
    return g

def resolve_attr(obj, attr):
    """A custom attrgetter that operates both on dictionaries and objects"""
    for name in attr.split("."):
        try:
            obj = getattr(obj, name)
        except AttributeError:
            obj = obj[name]
        except KeyError:
            raise ValueError('Object {0} has no attribute or key "{1}"'.format(obj, key))
    return obj

class DoesNotExist(ValueError):
    pass

class MultipleObjectsReturned(ValueError):
    pass

class QuerySet(object):
    def __init__(self, values):
        self.values = list(values)

    def __iter__(self):
        for value in self.values:
            yield value
        raise StopIteration

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, str(list(self.values)))

    def __getitem__(self, i):
        return self.values[i]

    def __eq__(self, other):
        return self.values == list(other)

    def _clone(self, new_values):
        return self.__class__(new_values)

    def _build_filter(self, **kwargs):
        """build a single filter function used to match arbitrary object"""

        def object_filter(obj):
            for key, value in kwargs.items():
                # we replace dango-like lookup by dots, so attrgetter can do his job
                key = key.replace('__', '.')

                getter = attrgetter(key)
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

        return self._clone(sorted(self.values, key=attrgetter(key), reverse=reverse))

    def all(self):
        return self._clone(self.values)

    def count(self):
        return len(self)

    def first(self):
        try:
            return self.values[0]
        except IndexError:
            return None

    def last(self):
        try:
            return self.values[-1]
        except IndexError:
            return None

    def filter(self, **kwargs):
        _filter = self._build_filter(**kwargs)
        return self._clone(filter(_filter, self.values))

    def exclude(self, **kwargs):
        _filter = self._build_filter(**kwargs)
        return self._clone(filter(lambda v: not _filter(v), self.values))

    def get(self, **kwargs):

        matches = self.filter(**kwargs)
        if len(matches) == 0:
            raise DoesNotExist()
        if len(matches) > 1:
            raise MultipleObjectsReturned()
        return matches[0]

class Manager(object):
    """Used to retrieve / order / filter preferences pretty much as django's ORM managers"""

    def __init__(self, values, queryset_class=QuerySet):
        self.values = values
        self.queryset_class = queryset_class

    def get_queryset(self):
        return self.queryset_class(self.values)

    def all(self):
        return self.get_queryset().all()

    def __getattr__(self, attr):
        try:
            return super(Manager, self).__getattr__(attr)
        except AttributeError:
            # Try to proxy on queryset if possible
            return getattr(self.get_queryset(), attr)
