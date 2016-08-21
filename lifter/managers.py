
class Manager(object):
    """Used to retrieve / order / filter preferences pretty much as django's ORM managers"""
    queryset_class = None

    def __init__(self, store, model, adapter, queryset_class=None, **kwargs):

        from . import query
        self.store = store
        self.model = model
        self.store = store
        self.queryset_class = queryset_class or self.queryset_class or query.QuerySet
        self.adapter = adapter
        if not self.adapter:
            self.adapter = self.store.get_default_adapter(model=self.model)

    def get_store(self):
        return self.store

    def get_queryset(self):
        return self.queryset_class(manager=self, model=self.model)

    def all(self):
        return self.get_queryset().all()

    def execute(self, query):
        return self.store._execute(query, model=self.model, adapter=self.adapter)

    def __getattr__(self, attr):
        # Try to proxy on queryset if possible
        return getattr(self.get_queryset(), attr)
