
from lifter.backends import python
from lifter import models
from django.db.models import QuerySet


def _locally(self):
    store = python.IterableStore(self)
    return store.query(models.Model)

def setup():
    """
    This is a bit dirty, but to make lifter available on django querysets,
    we simply add a custom method to django base queryset class.
    """

    method_name = 'locally'
    setattr(QuerySet, method_name, _locally)
