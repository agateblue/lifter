import re

from . import models
from . import utils

class Adapter(object):
    def __init__(self, attributes_converter=utils.to_snake_case):
        self.attributes_converter = attributes_converter

    def parse(self, data, model):
        raw_data = self.get_raw_data(data, model)
        raw_data = self.convert_attribute_names(raw_data)
        cleaned_data = self.full_clean(raw_data, model)
        return model(**cleaned_data)

    def convert_attribute_names(self, data):
        if not self.attributes_converter:
            return data

        return {
            self.attributes_converter(key): value
            for key, value in data.items()
        }

    def full_clean(self, data, model):
        return self.clean(self._clean_fields(data, model), model)

    def clean(self, data, model):
        return data

    def _clean_fields(self, data, model):
        cleaned_data = {}
        for key, value in data.items():
            cleaner = 'clean_{0}'.format(key)
            field = model._meta.fields.get(key, None)
            if hasattr(self, cleaner):
                cleaned_data[key] = getattr(self, cleaner)(data, value, model, field)
            else:
                if field:
                    # We use the default field conversion
                    cleaned_data[key] = field.to_python(self, value)
                else:
                    cleaned_data[key] = value
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

    def get_raw_data(self, data, model):
        if self.key:
            to_convert = data[self.key]
        else:
            to_convert = data

        if self.recursive:
            # we convert subdirectories to proper model instances
            for key, value in to_convert.items():
                if isinstance(value, dict):
                    to_convert[key] = self.parse(value, models.Model)
        return to_convert

class RegexAdapter(Adapter):
    def __init__(self, *args, **kwargs):
        self.regex = kwargs.pop('regex', self.regex)

        super(RegexAdapter, self).__init__(*args, **kwargs)

        self.compiled_regex = re.compile(self.regex)

    def get_raw_data(self, data, model):
        match = self.compiled_regex.match(data)
        return match.groupdict()
