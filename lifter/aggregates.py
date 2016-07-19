from . import utils


class Aggregate(object):
    def __init__(self, attr_name, **kwargs):
        self.attr_name = attr_name

    @property
    def identifier(self):
        return '{0}__{1}'.format(self.attr_name, self.name)

    def aggregate(self, values):
        raise NotImplementedError

    def __hash__(self):
        return hash((self.attr_name,))
        
class Sum(Aggregate):
    name = 'sum'

    def aggregate(self, values):
        return sum(values)


class Min(Aggregate):
    name = 'min'

    def aggregate(self, values):
        return min(values)

class Max(Aggregate):
    name = 'max'

    def aggregate(self, values):
        return max(values)

class Avg(Aggregate):
    name = 'avg'

    def aggregate(self, values):
        return float(sum(values)) / len(values)
