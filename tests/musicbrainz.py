from lifter import models, query, adapters
from lifter.backends import http

import xml.etree.ElementTree as ET


class Release(models.BaseModel):
    title = models.Field()
    date = models.Field()

class MBRefinedStore(http.HTTPRefinedStore):
    def clean_data(self, data):
        return ET.fromstring(data)[0]

    def build_endpoint_url(self):
        base = self.parent.protocol + '://' + self.parent.endpoint
        return base + self.model.__name__.lower()

    def handle_search(self, query):
        url = self.build_endpoint_url()
        request = self.request_factory('GET', url, params={'query': query.hints['querystring']})
        response = self.parent.session.send(request)
        return self.parse_results(response.content, query)

class MBStore(http.HTTPStore):
    refined_class = MBRefinedStore
    endpoint = 'musicbrainz.org/ws/2/'

class ReleaseQuerySet(query.QuerySet):
    def search(self, querystring):
        query = self.query.clone(action='search', querystring=querystring)
        return self.manager.execute(query)

class ReleaseAdapter(adapters.Adapter):
    namespaces = {
        'mb': 'http://musicbrainz.org/ns/mmd-2.0#'
    }
    def get_raw_data(self, data):
        return {
            'title': data.find('mb:title', namespaces=self.namespaces).text,
            'date': data.find('mb:date', namespaces=self.namespaces).text,
        }


class Client(object):
    def __init__(self, session=None, protocol='http'):
        self.session = session
        self.store = MBStore(protocol=protocol, session=self.session)
        self.releases = self.store.query(Release, adapter=ReleaseAdapter(), queryset_class=ReleaseQuerySet)
