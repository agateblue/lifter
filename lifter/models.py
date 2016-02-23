
from . import query

class BaseModelMeta(type):
    def __getattr__(cls, key):
        return getattr(query.Path(), key)

class BaseModel(object):
    __metaclass__ = BaseModelMeta

    @classmethod
    def load(cls, values):
        return query.QuerySet(values)

def Model(name):
    return BaseModelMeta(name, (BaseModel,), {})
