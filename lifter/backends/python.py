
from . import base
from .. import query
from .. import exceptions
from .. import utils
from .. import managers


class PythonPath(query.Path):
    pass

class PythonModel(base.BaseModel):
    __metaclass__ = base.BaseModelMeta
    path_class = PythonPath

    @classmethod
    def load(cls, values):
        return PythonManager(values=values, model=cls)

class PythonManager(managers.Manager):

    def __init__(self, *args, **kwargs):
        self._values = kwargs.pop('values')
        super(PythonManager, self).__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        final_query = self.build_query(*args, **kwargs)
        first_match = None
        for match in filter(final_query, self.data):
            # Little hack to avoid looping over the whole results set
            if not first_match:
                first_match = match
                continue
            raise exceptions.MultipleObjectsReturned()

        if not first_match:
            raise exceptions.DoesNotExist()

        return first_match


    def _raw_data_iterator(self, query):
        if not query:
            for obj in self._values:
                yield obj
        else:
            for obj in self._values:
                if query._test(obj):
                    yield obj
        # return filter(self.query, self._iter_data)

    def execute_query(self, query, orderings, **kwargs):
        iterator = self._raw_data_iterator(query)

        if orderings:
            random_value = lambda v: random.random()

            for ordering in reversed(orderings):
                # We loop in reverse order because we found no other way to handle multiple sorting
                # in different directions right now

                if ordering.random:
                    iterator = sorted(iterator, key=random_value)
                    continue
                iterator = sorted(iterator, key=ordering.path.get, reverse=ordering.reverse)

        if kwargs.get('distinct', False):
            iterator = utils.unique_everseen(iterator)
        return iterator

    def values_list(self, paths, *args, **kwargs):
        data = self.execute_query(kwargs['query'], kwargs['orderings'])
        if kwargs.get('flat', False):
            getter = lambda val: paths[0].get(val)
        else:
            getter = lambda val: tuple(path.get(val) for path in paths)

        return PythonModel.load(map(getter, data)).all()

    def values(self, paths, *args, **kwargs):
        data = self.execute_query(kwargs['query'], kwargs['orderings'])
        return PythonModel.load(map(
                lambda val: {str(path):path.get(val) for path in paths},
                data
            )
        ).all()
