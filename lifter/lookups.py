import persisting_theory
import operator

class Lookups(persisting_theory.Registry):
    def prepare_name(self, data, name):
        data.registry_name = name
        return name

registry = Lookups()
register = registry.register


class BaseLookup(object):
    def __call__(self, value):
        return self.lookup(value)

    def lookup(self, value):
        raise NotImplementedError

class OneValueLookup(BaseLookup):
    operator = None
    def __init__(self, value):
        self.reference_value = value

    def __str__(self):
        return '{0} {1}'.format(self.operator, self.reference_value)

@register(name='eq')
class eq(OneValueLookup):
    operator = '=='
    def lookup(self, value):
        return value == self.reference_value

@register(name='ne')
class ne(OneValueLookup):
    operator = '!='
    def lookup(self, value):
        return value != self.reference_value

@register(name='gt')
class gt(OneValueLookup):
    operator = '>'
    def lookup(self, value):
        return value > self.reference_value

@register(name='gte')
class gte(OneValueLookup):
    operator = '>='
    """Greater than or equal"""
    def lookup(self, value):
        return value >= self.reference_value

@register(name='lt')
class lt(OneValueLookup):
    operator = '<'
    def lookup(self, value):
        return value < self.reference_value

@register(name='lte')
class lte(OneValueLookup):
    operator = '<='
    def lookup(self, value):
        return value <= self.reference_value

@register(name='startswith')
class startswith(OneValueLookup):
    operator = 'startswith'
    def lookup(self, value):
        return value.startswith(self.reference_value)

@register(name='istartswith')
class istartswith(OneValueLookup):
    operator = 'istartswith'
    def lookup(self, value):
        return value.lower().startswith(self.reference_value.lower())

@register(name='endswith')
class endswith(OneValueLookup):
    operator = 'endswith'
    def lookup(self, value):
        return value.endswith(self.reference_value)

@register(name='iendswith')
class iendswith(OneValueLookup):
    operator = 'iendswith'
    def lookup(self, value):
        return value.lower().endswith(self.reference_value.lower())

@register(name='contains')
class contains(OneValueLookup):
    operator = 'contains'
    def lookup(self, value):
        return self.reference_value in value

@register(name='icontains')
class icontains(OneValueLookup):
    operator = 'icontains'
    def lookup(self, value):
        return self.reference_value.lower() in value.lower()

@register(name='value_in')
class value_in(OneValueLookup):
    operator = 'in'
    def lookup(self, value):
        return value in self.reference_value

@register(name='exists')
class exists(BaseLookup):
    def lookup(self, value):
        from .query import Path
        return value != Path.DoesNotExist

@register(name='value_range')
class value_range(OneValueLookup):
    operator = 'in range'
    def __init__(self, range_iterable):
        self.start, self.end = range_iterable

    def lookup(self, value):
        return value >= self.start and value <= self.end

@register(name='test')
class test(BaseLookup):
    def __init__(self, test, *args, **kwargs):
        self.test = test
        self.args = args
        self.kwargs = kwargs

    def lookup(self, value):
        return self.test(value, *self.args, **self.kwargs)
