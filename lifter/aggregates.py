from . import utils


class Aggregate(object):
    def __init__(self, attr_name, **kwargs):
        self.attr_name = attr_name

    @property
    def identifier(self):
        return '{0}__{1}'.format(self.attr_name, self.name)

    def aggregate(self, values):
        raise NotImplementedError

class Sum(Aggregate):
    name = 'sum'

    def aggregate(self, values):
        getter = utils.attrgetter(self.attr_name)
        return sum([getter(v) for v in values])


class Min(Aggregate):
    name = 'min'

    def aggregate(self, values):
        getter = utils.attrgetter(self.attr_name)
        return min([getter(v) for v in values])

class Max(Aggregate):
    name = 'max'

    def aggregate(self, values):
        getter = utils.attrgetter(self.attr_name)
        return max([getter(v) for v in values])

class Avg(Aggregate):
    name = 'avg'

    def aggregate(self, values):
        getter = utils.attrgetter(self.attr_name)
        total = sum([getter(v) for v in values])
        return float(total) / len(values)
