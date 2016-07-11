from . import managers


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

    def get_manager(self, **kwargs):
        return self.manager_class(model=self.model, store=self, **kwargs)
