

class Field(object):
    def __init__(self, store_field=None):
        self.store_field = store_field

    def to_python(self, adapter, field, value, model_field):
        return value


class DeferredForeignKey(Field):
    def __init__(self, adapter, **kwargs):
        self.adapter = adapter
        super(DeferredForeignKey, self).__init__(**kwargs)

    def to_python(self, adapter, field, value, store, model_field):
        model = model_field.to
        m = model()
        m._set_primary_key(value)
        m._set_deferred(store=store, adapter=adapter)

        return m
