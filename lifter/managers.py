
class Manager(object):
    """Used to retrieve / order / filter preferences pretty much as django's ORM managers"""

    def __init__(self, values, model, queryset_class=None):

        from . import query
        self.model = model
        self._values = values
        self.queryset_class = queryset_class or query.QuerySet

    def get_queryset(self):
        return self.queryset_class(self._values, model=self.model)

    def all(self):
        return self.get_queryset().all()

    def __getattr__(self, attr):
        try:
            return super(Manager, self).__getattr__(attr)
        except AttributeError:
            # Try to proxy on queryset if possible
            return getattr(self.get_queryset(), attr)
