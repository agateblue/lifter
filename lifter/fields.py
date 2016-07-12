import datetime


class Field(object):
    def __init__(self, primary_key=False):
        self.primary_key = primary_key

class DateField(Field):

    def default_to_python(self, adapter, v, date_format="%Y-%m-%d"):
        return datetime.datetime.strptime(v, date_format).date()

class CharField(Field):
    def default_to_python(self, adapter, v):
        return v


class ForeignKey(Field):
    def __init__(self, model, **kwargs):
        self.model = model
        super(ForeignKey, self).__init__(**kwargs)

    def default_to_python(self, adapter, v):
        return self.adapter.store.adapters[self.model].clean(v)
