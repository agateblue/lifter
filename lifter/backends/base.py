
class BaseModelMeta(type):
    def __getattr__(cls, key):
        return getattr(cls.path_class(), key)

class BaseModel(object):
    __metaclass__ = BaseModelMeta
