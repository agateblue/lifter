import hashlib

from . import managers
from . import adapters
from . import exceptions
from . import models
from . import query
from . import utils


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


def cast_to_values(query, results):
    from .backends.python import IterableStore
    if query.hints['mode'] == 'mapping':
        getter = lambda val: {str(path): path_to_value(val, path) for path in query.hints['paths']}
    else:
        if query.hints.get('flat', False):
            getter = lambda val: path_to_value(val, query.hints['paths'][0])
        else:
            getter = lambda val: tuple(path_to_value(val, path) for path in query.hints['paths'])
    values = map(getter, results)

    return IterableStore(values).query(models.Model).all()


class Store(object):
    """
    A place to look for data (python iterable, database, rest api...)

    The manager will apply the query on the store to return results
    """
    manager_class = managers.Manager

    def __init__(self, cache=None, identifier=None):
        self.cache = cache
        self.identifier = identifier
        if self.cache and not self.identifier:
            raise ValueError('You must provide a unique identifier if you want to use caching')

    def query(self, model, adapter=None, **kwargs):
        return self.get_manager(model=model, store=self, adapter=adapter, **kwargs)

    def get_manager(self, **kwargs):
        return self.manager_class(**kwargs)

    def get_default_adapter(self, model):
        return adapters.DictAdapter(recursive=True)

    def get_cache_key(self, query, model):
        return ':'.join([
            self.identifier,
            str(model._meta.app_name),
            model._meta.name,
            self.hash_query(query)
        ])

    def get_from_cache(self, query, model):
        key = self.get_cache_key(query, model)
        return self.cache.get(key, reraise=True)

    def set_in_cache(self, query, model, value):
        key = self.get_cache_key(query, model)
        return self.cache.set(key, value)

    def _execute(self, query, model, adapter, raw=False):
        try:
            if self.cache:
                return self.get_from_cache(query, model)
        except (exceptions.NotInCache, exceptions.DisabledCache):
            pass

        try:
            handler = getattr(self, 'handle_{0}'.format(query.action))
        except AttributeError:
            raise ValueError('Unsupported {0} action'.format(query.action))

        raw_results = handler(query, model)

        if self.cache:
            self.set_in_cache(query, model, raw_results)

        if raw:
            return raw_results

        if query.action == 'count':
            return raw_results

        if query.action == 'values':
            return cast_to_values(query, raw_results)

        return self._parse_results(
            query, raw_results, adapter=adapter, model=model)

    def _parse_results(self, query, results, model, adapter):
        if query.hints.get('force_single', False):
            length = len(results)
            if length > 1:
                raise exceptions.MultipleObjectsReturned()
            if length == 0:
                raise exceptions.DoesNotExist()
            if adapter:
                return adapter.parse(results[0], model)

            return results[0]
        else:
            if adapter:
                return [adapter.parse(result, model)
                        for result in results]
            return results

    def hash_query(self, query):
        h = hash(query)
        return hashlib.sha512(str(h).encode('utf-8')).hexdigest()[:20]
