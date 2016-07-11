import requests
from .. import store



class HTTPStore(store.Store):
    def __init__(self, *args, **kwargs):
        self._session = kwargs.pop('session', None) or requests.Session()
        self.protocol = kwargs.pop('protocol', 'http')
        super(HTTPStore, self).__init__()

    def request_factory(self, method, url, headers={}, **kwargs):
        return requests.Request(method, url, headers=headers, **kwargs).prepare()

    def get_parser(self):
        return self.parser or self.parser_class()

    def parse_results(self, data, query):
        # first, we parse the whole data to a proper python iterable we'll then pass
        # to a dedicated parser
        cleaned_data = self.clean_data(data)
        parser = query.hints['parser']
        model = query.hints['model']
        return [model(**parser.parse(row)) for row in cleaned_data]

    @property
    def session(self):
        return self._session
