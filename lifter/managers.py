
class Manager(object):
    """Used to retrieve / order / filter preferences pretty much as django's ORM managers"""

    def __init__(self, model, queryset_class=None, **kwargs):

        from . import query
        self.model = model
        self.queryset_class = queryset_class or query.QuerySet

    def get_queryset(self):
        return self.queryset_class(manager=self, model=self.model)

    def all(self):
        return self.get_queryset().all()

    def values_list(self, *args, **kwargs):
        raise NotImplementedError()
    
    def values(self, *args, **kwargs):
        raise NotImplementedError()

    def __getattr__(self, attr):
        try:
            return super(Manager, self).__getattr__(attr)
        except AttributeError:
            # Try to proxy on queryset if possible
            return getattr(self.get_queryset(), attr)
