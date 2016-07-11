import requests
from .. import store



class HTTPRefinedStore(store.RefinedStore):

    def parse_results(self, data, query):
        # first, we parse the whole data to a proper python iterable we'll then pass
        # to a dedicated adapter
        cleaned_data = self.clean_data(data)
        return [self.model(**self.adapter.parse(row)) for row in cleaned_data]


    def request_factory(self, method, url, headers={}, **kwargs):
        return requests.Request(method, url, headers=headers, **kwargs).prepare()


class HTTPStore(store.Store):
    def __init__(self, *args, **kwargs):
        self._session = kwargs.pop('session', None) or requests.Session()
        self.protocol = kwargs.pop('protocol', 'http')
        super(HTTPStore, self).__init__()

    @property
    def session(self):
        return self._session
