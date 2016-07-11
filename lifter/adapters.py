import re


class Adapter(object):
    def parse(self, data):
        raw_data = self.get_raw_data(data)
        cleaned_data = self.full_clean(raw_data)
        return cleaned_data

    def full_clean(self, data):
        return self.clean(self._clean_fields(data))

    def clean(self, data):
        return data

    def _clean_fields(self, data):
        cleaned_data = {}
        for key, value in data.items():
            cleaner = 'clean_{0}'.format(key)
            if hasattr(self, cleaner):
                cleaned_data[key] = getattr(self, cleaner)(value)
            else:
                cleaned_data[key] = value
        return cleaned_data

class RegexAdapter(Adapter):
    def __init__(self, regex=None):
        self.regex = regex or self.regex
        self.compiled_regex = re.compile(self.regex)

    def get_raw_data(self, data):
        match = self.compiled_regex.match(data)
        return match.groupdict()
