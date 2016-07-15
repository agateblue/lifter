from . import managers
from . import adapters
from . import exceptions
from . import models
from . import query
from . import utils


def cast_results_to_model(f):
    def wrapper(self, query, *args, **kwargs):
        results = f(self, query, *args, **kwargs)
        if query.hints.get('force_single', False):
            length = len(results)
            if length > 1:
                raise exceptions.MultipleObjectsReturned()
            if length == 0:
                raise exceptions.DoesNotExist()
            return self.adapter.parse(results[0], self.model)
        else:
            return [self.adapter.parse(result, self.model)
                    for result in results]
    return wrapper


def path_to_value(data, path, **kwargs):
    soft_fail = kwargs.pop('soft_fail', False)
    getters = [utils.attrgetter(part) for part in path.path]

    try:
        for getter in getters:
            data = getter(data)
    except exceptions.MissingAttribute:
        if soft_fail:
            return query.Path.DoesNotExist
        raise
    return data

def cast_to_values(f):

    def wrapper(self, query):
        from .backends.python import IterableStore
        results = f(self, query)
        if query.hints['mode'] == 'mapping':
            getter = lambda val: {str(path): path_to_value(val, path) for path in query.hints['paths']}
        else:
            if query.hints.get('flat', False):
                getter = lambda val: path_to_value(val, query.hints['paths'][0])
            else:
                getter = lambda val: tuple(path_to_value(val, path) for path in query.hints['paths'])
        values = map(getter, results)

        return IterableStore(values).query(models.Model).all()

    return wrapper
    
class Store(object):
    """
    A place to look for data (python iterable, database, rest api...)

    The manager will apply the query on the store to return results
    """

    def get_refined_store_class(self, model, adapter=None):
        return self.refined_class

    def refine(self, model, adapter=None):
        kls = self.get_refined_store_class(model, adapter)
        return kls(
            parent=self,
            model=model,
            adapter=adapter,
            **self.get_refine_kwargs(model, adapter)
        )
    def query(self, model, adapter=None, **kwargs):
        return self.refine(model, adapter).get_manager(**kwargs)

    def get_refine_kwargs(self, model, adapter):
        return {}


class RefinedStore(object):
    manager_class = managers.Manager

    def __init__(self, parent, model, adapter):
        self.parent = parent
        self.model = model
        self.adapter = adapter
        if not self.adapter:
            self.adapter = self.get_default_adapter()

    def get_default_adapter(self):
        return adapters.DictAdapter(recursive=True)

    def get_manager(self, **kwargs):
        return self.manager_class(model=self.model, store=self, **kwargs)
