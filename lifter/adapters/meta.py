import six
from .fields import Field


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


class Meta(object):
    def __init__(self, fields):
        self.fields = fields


class BaseAdapterMeta(type):
    def __new__(cls, name, bases, attrs):
        meta_kwargs = {}
        meta_kwargs['fields'] = setup_fields(attrs)
        meta = Meta(**meta_kwargs)
        attrs['_meta'] = meta
        return super(BaseAdapterMeta, cls).__new__(cls, name, bases, attrs)


class BaseAdapter(six.with_metaclass(BaseAdapterMeta, object)):
    pass
