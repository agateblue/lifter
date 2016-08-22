import six

from .. import managers
from .. import query
from ..fields import Field


class Deferred(object):
    pass

DEFERRED = Deferred()

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
    _deferred = False
    _store = None

    @classmethod
    def load(cls, store, **kwargs):
        return store.query(cls, **kwargs)

    def __init__(self, **kwargs):
        for field_name, value in kwargs.items():
            setattr(self, field_name, value)

    def _get_primary_key_field(self):
        try:
            return [
                field_name for field_name, field in self._meta.fields.items()
                if field.primary_key
            ][0]
        except IndexError:
            raise ValueError('No primary key field declared on this model')

    def _set_primary_key(self, pk):
        setattr(self, self._get_primary_key_field(), pk)

    def _set_deferred(self, store, adapter):
        """
        Will loop over availble fields and mark them as deferred
        if the field is accessed later, deferred field will be resolved from
        given store
        """
        self._store = store
        self._adapter = adapter
        self._deferred = True
        for field_name, field in self._meta.fields.items():
            if field.primary_key:
                continue
            setattr(self, field_name, DEFERRED)

    def __getattribute__(self, attr):
        value = super(BaseModel, self).__getattribute__(attr)
        if value == DEFERRED:
            self._refresh_from_store()
            return getattr(self, attr)
        return value

    def _refresh_from_store(self):
        """
        Refresh model fields by requesting the store
        this will remove the _deferred flag and reset any deferred value
        to None to prevent infinite recursion
        """
        self._deferred = False
        manager = self._store.query(self.__class__, adapter=self._adapter)
        primary_key_field = self._get_primary_key_field()
        lookup = {
            primary_key_field: getattr(self, primary_key_field)
        }
        fresh = manager.get(**lookup)
        for field_name in self._meta.fields:
            setattr(self, field_name, getattr(fresh, field_name))
