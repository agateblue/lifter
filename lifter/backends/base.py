import six

from .. import managers
from .. import query


class BaseModelMeta(type):
    def __getattr__(cls, key):
        return getattr(query.Path(), key)

class BaseModel(six.with_metaclass(BaseModelMeta, object)):

    @classmethod
    def load(cls, store, **kwargs):
        return store.query(cls, **kwargs)

    def __init__(self, **kwargs):
        for field_name, value in kwargs.items():
            setattr(self, field_name, value)
