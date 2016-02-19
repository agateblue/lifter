
import operator

def need_flattening(value):
    try:
        return isinstance(value[0], IterableAttr)
    except (IndexError, TypeError):
        return False

def flatten(root):
    """Resolve of attributes into a flat list so we can run a lookup against each of these values"""
    if isinstance(root, IterableAttr):
        for value in root._items:
            if need_flattening(value):
                for subvalue in flatten(value):
                    yield subvalue
            else:
                yield value

    else:
        yield root



class IterableAttr(object):

    def __init__(self, iterable, key):
        self._key = key
        self._items = [item[key] for item in iterable]

    def __repr__(self):
        REPR_OUTPUT_SIZE = 10
        data = list(self._items[:REPR_OUTPUT_SIZE + 1])
        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."
        return '<IterableAttr %r>' % data

    def __len__(self):
        return len(self._items)

    def __getitem__(self, key):
        return self.__class__(self._items, key)


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
    attr = attr.replace('__', '.') # replace lookups
    for name in attr.split("."):
        try:
            obj = getattr(obj, name)
        except AttributeError:
            try:
                try:
                    obj = obj[name]
                except TypeError:
                    obj = IterableAttr(obj, name)
            except (KeyError, TypeError):
                raise ValueError('Object {0} has no attribute or key "{1}"'.format(obj, name))
    return obj

def unique_everseen(seq):
    """Solution found here : http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order"""
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
