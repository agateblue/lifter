import re
import operator

from . import exceptions


class IterableAttr(object):

    def __init__(self, iterable, key):
        self._items = [item[key] for item in iterable]

    def __eq__(self, other):
        return other in self._items

    def __getitem__(self, key):
        return self.__class__(self._items, key)


def attrgetter(*items):

    if len(items) == 1:
        attr = items[0]
        def g(obj):
            return resolve_attr(obj, attr)
    else:
        def g(obj):
            return tuple(resolve_attr(obj, attr) for attr in items)
    return g

def resolve_attr(obj, name):
    """A custom attrgetter that operates both on dictionaries and objects"""
    # TODO: setup some hinting, so we can go directly to the correct
    # Maybe it's a dict ? Let's try dict lookup, it's the fastest
    try:
        return obj[name]
    except TypeError:
        pass
    except KeyError:
        raise exceptions.MissingField('Dict {0} has no attribute or key "{1}"'.format(obj, name))

    # Okay, it's not a dict, what if we try to access the value as for a regular object attribute?
    try:
        # Slight hack for better speed, since accessing dict is fast
        return obj.__dict__[name]
    except (KeyError, AttributeError):
        pass

    try:
        # Lookup using regular attribute
        return getattr(obj, name)
    except AttributeError:
        pass

    # Last possible choice, it's an iterable
    try:
        return IterableAttr(obj, name)
    except TypeError:
        raise exceptions.MissingField('Object {0} has no attribute or key "{1}"'.format(obj, name))


def unique_everseen(seq):
    """Solution found here : http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order"""
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def to_snake_case(s):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def to_camel_case(s):
    new_s = ''.join(x.capitalize() or '_' for x in s.split('_'))
    lower_first_letter = lambda s: s[:1].lower() + s[1:] if s else ''
    return lower_first_letter(new_s)
