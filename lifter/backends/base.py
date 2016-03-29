
class BaseModelMeta(type):
    def __getattr__(cls, key):
        return getattr(cls.path_class(), key)

class BaseModel(object):
    __metaclass__ = BaseModelMeta

    def __init__(self, **kwargs):
        for field_name, value in kwargs.items():
            setattr(self, field_name, value)
