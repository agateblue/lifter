import re


class Adapter(object):
    def parse(self, data, model):
        raw_data = self.get_raw_data(data, model)
        cleaned_data = self.full_clean(raw_data, model)
        return model(**cleaned_data)

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

class RegexAdapter(Adapter):
    def __init__(self, regex=None):
        self.regex = regex or self.regex
        self.compiled_regex = re.compile(self.regex)

    def get_raw_data(self, data, model):
        match = self.compiled_regex.match(data)
        return match.groupdict()
