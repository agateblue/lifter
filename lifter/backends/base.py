import six

from .. import managers
from .. import query
from ..fields import Field


class Meta(object):
    """Much like django Model.Meta"""
    def __init__(self, fields, name, name_plural=None, app_name=None):
        self.fields = fields
        self.app_name = app_name
        self.name = name
        if not name_plural:
            self.name_plural = self.name + 's'
        else:
            self.name_plural = name_plural


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


META_ALLOWED_FIELDS = [
    'name',
    'name_plural',
    'app_name',
]
class BaseModelMeta(type):
    def __new__(cls, name, bases, attrs):
        declared_meta = attrs.get('Meta')
        meta_kwargs = {

        }
        if declared_meta:
            # a class Meta was found on the model class
            for field in META_ALLOWED_FIELDS:
                meta_kwargs[field] = getattr(declared_meta, field, None)

        meta_kwargs['fields'] = setup_fields(attrs)
        if not meta_kwargs.get('name', None):
            meta_kwargs['name'] = name.lower()
        meta = Meta(**meta_kwargs)
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
