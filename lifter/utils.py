
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
