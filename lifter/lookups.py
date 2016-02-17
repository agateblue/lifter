
class BaseLookup(object):
    def __call__(self, value):
        return self.lookup(value)

    def lookup(self, value):
        raise NotImplementedError

class OneValueLookup(BaseLookup):
    def __init__(self, value):
        self.reference_value = value

class gt(OneValueLookup):
    """Greater than"""
    def lookup(self, value):
        return value > self.reference_value

class gte(OneValueLookup):
    """Greater than or equal"""
    def lookup(self, value):
        return value >= self.reference_value

class lt(OneValueLookup):
    """Less than"""
    def lookup(self, value):
        return value < self.reference_value

class lte(OneValueLookup):
    """Less than or equal"""
    def lookup(self, value):
        return value <= self.reference_value

class startswith(OneValueLookup):
    def lookup(self, value):
        return value.startswith(self.reference_value)

class istartswith(OneValueLookup):
    def lookup(self, value):
        return value.lower().startswith(self.reference_value.lower())

class endswith(OneValueLookup):
    def lookup(self, value):
        return value.endswith(self.reference_value)

class iendswith(OneValueLookup):
    def lookup(self, value):
        return value.lower().endswith(self.reference_value.lower())

class contains(OneValueLookup):
    def lookup(self, value):
        return self.reference_value in value

class icontains(OneValueLookup):
    def lookup(self, value):
        return self.reference_value.lower() in value.lower()

class value_in(OneValueLookup):
    def lookup(self, value):
        return value in self.reference_value

class value_range(BaseLookup):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def lookup(self, value):
        return value >= self.start and value <= self.end
