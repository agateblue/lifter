import re

from .. import models
from .. import utils
from . import meta
from .fields import *


class Adapter(meta.BaseAdapter):
    def __init__(self, attributes_converter=utils.to_snake_case):
        self.attributes_converter = attributes_converter

    def get_raw_data(self, data, model, store):
        return data

    def parse(self, data, model, store):
        raw_data = self.get_raw_data(data, model, store)
        raw_data = self.convert_attribute_names(raw_data)
        cleaned_data = self.full_clean(raw_data, model, store)
        return model(**cleaned_data)

    def convert_attribute_names(self, data):
        if not self.attributes_converter:
            return data

        return {
            self.attributes_converter(key): value
            for key, value in data.items()
        }

    def full_clean(self, data, model, store):
        return self.clean(self._clean_fields(data, model, store), model, store)

    def clean(self, data, model, store):
        return data

    def _clean_field(self, data, model, field, value, store, use_model=False):
        cleaner = 'clean_{0}'.format(field)
        if hasattr(self, cleaner):
            return getattr(self, cleaner)(data, value, model, field)

        model_field = model._meta.fields.get(field, None)
        if use_model and model_field:
            # We use the default field conversion
            return model_field.to_python(self, value)

        return value

    def _clean_fields(self, data, model, store):
        cleaned_data = {}
        if self._meta.fields:
            # we have some fields explicitely declared on teh adapter
            # we use those fields to retrieve the final values
            for field_name, field in self._meta.fields.items():
                value = self._clean_field(
                    data=data,
                    model=model,
                    field=field_name,
                    value=data[field.store_field or field_name],
                    store=store,
                    use_model=False,
                )
                cleaned_data[field_name] = field.to_python(
                    adapter=self,
                    value=value,
                    field=field_name,
                    store=store,
                    model_field=model._meta.fields.get(field_name),
                )
        else:
            # nothing was declared on the adapter, we just try to clean any
            # passed value
            for key, value in data.items():
                cleaned_data[key] = self._clean_field(
                    data=data,
                    model=model,
                    field=key,
                    value=value,
                    store=store,
                    use_model=True,
                )
        return cleaned_data


class DictAdapter(Adapter):
    """
    Dummy adapter that simply map dictionary keys to model attributes
    """
    def __init__(self, *args, **kwargs):
        self.recursive = kwargs.pop('recursive', True)
        # if any, we'll map only attributes under the given key
        self.key = kwargs.pop('key', None)
        super(DictAdapter, self).__init__(*args, **kwargs)

    def get_raw_data(self, data, model, store):
        if self.key:
            to_convert = data[self.key]
        else:
            to_convert = data

        if self.recursive:
            # we convert subdictionaries to proper model instances
            for key, value in to_convert.items():
                if isinstance(value, dict):
                    to_convert[key] = self.parse(value, models.Model, store)
        return to_convert


class RegexAdapter(Adapter):
    def __init__(self, *args, **kwargs):
        self.regex = kwargs.pop('regex', self.regex)

        super(RegexAdapter, self).__init__(*args, **kwargs)

        self.compiled_regex = re.compile(self.regex)

    def get_raw_data(self, data, model, store):
        match = self.compiled_regex.match(data)
        return match.groupdict()


class ETreeAdapter(Adapter):

    def get_raw_data(self, data, model, store):

        return {
            self.tag_to_field_name(e.tag): e.text
            for e in data
        }

    def tag_to_field_name(self, tag):
        """
        Since the tag may be fully namespaced, we want to strip the namespace
        information
        """
        return tag.split('}')[-1]
