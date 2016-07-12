import six

from .. import managers
from .. import query
from ..fields import Field


class Meta(object):
    """Much like django Model.Meta"""
    def __init__(self, fields):
        self.fields = fields

def setup_fields(attrs):
    """
    Collect all fields declared on the class and remove them from attrs
    """
    fields = {}
    iterator = list(attrs.items())
    for key, value in iterator:
        if not isinstance(value, Field):
            continue
        fields[key] = value
        del attrs[key]
    return fields

class BaseModelMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = setup_fields(attrs)
        meta = Meta(fields=fields)
        attrs['_meta'] = meta
        return super(BaseModelMeta, cls).__new__(cls, name, bases, attrs)


    def __getattr__(cls, key):
        return getattr(query.Path(), key)

class BaseModel(six.with_metaclass(BaseModelMeta, object)):

    @classmethod
    def load(cls, store, **kwargs):
        return store.query(cls, **kwargs)

    def __init__(self, **kwargs):
        for field_name, value in kwargs.items():
            setattr(self, field_name, value)
