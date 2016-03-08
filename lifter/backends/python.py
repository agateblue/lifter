
from . import base
from .. import query
from .. import exceptions
from .. import utils


class PythonPath(query.Path):
    pass

class PythonModel(base.BaseModel):
    __metaclass__ = base.BaseModelMeta
    path_class = PythonPath

    @classmethod
    def load(cls, values):
        return PythonQuerySet(values, model=cls)

class PythonQuerySet(query.QuerySet):

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


    def _raw_data_iterator(self):
        if not self.query:
            for obj in self._iter_data:
                yield obj
        else:
            for obj in self._iter_data:
                if self.query._test(obj):
                    yield obj
        # return filter(self.query, self._iter_data)

    def execute_query(self):
        iterator = self._raw_data_iterator()

        if self.orderings:
            random_value = lambda v: random.random()

            for ordering in reversed(self.orderings):
                # We loop in reverse order because we found no other way to handle multiple sorting
                # in different directions right now

                if ordering.random:
                    iterator = sorted(iterator, key=random_value)
                    continue
                iterator = sorted(iterator, key=ordering.path.get, reverse=ordering.reverse)

        return iterator

    def distinct(self):
        return self._clone(utils.unique_everseen(self.data))

    def backend_values_list(self, paths, flat=False):
        if flat:
            getter = lambda val: paths[0].get(val)
        else:
            getter = lambda val: tuple(path.get(val) for path in paths)

        return self._clone(  # I believe in this case we should return raw data not query_set
            map(getter, self.data)
        )

    def backend_values(self, paths):
        return self._clone(  # I believe in this case we should return raw data not query_set
            map(
                lambda val: {str(path):path.get(val) for path in paths},
                self.data
            )
        )
