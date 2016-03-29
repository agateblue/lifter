from lifter import models, query, parsers
from lifter.backends import http

import xml.etree.ElementTree as ET


class Release(models.BaseModel):
    title = models.Field()
    date = models.Field()


class ReleaseQuerySet(query.QuerySet):
    def search(self, querystring):
        query = self.query.clone(action='search', querystring=querystring)
        return self.manager.execute(query)

class ReleaseParser(parsers.Parser):
    namespaces = {
        'mb': 'http://musicbrainz.org/ns/mmd-2.0#'
    }
    def get_raw_data(self, data):
        return {
            'title': data.find('mb:title', namespaces=self.namespaces).text,
            'date': data.find('mb:date', namespaces=self.namespaces).text,
        }

class ReleaseManager(http.HTTPManager):
    queryset_class = ReleaseQuerySet
    endpoint = 'musicbrainz.org/ws/2/release'
    parser_class = ReleaseParser

    def clean_data(self, data):
        return ET.fromstring(data)[0]

    def handle_search(self, query):
        url = self.protocol + '://' + self.endpoint
        request = self.request_factory('GET', url, params={'query': query.hints['querystring']})
        response = self.session.send(request)
        return self.parse_results(response.content)

class Client(object):
    def __init__(self, session=None, protocol='http'):
        self.session = session
        self.releases = ReleaseManager(model=Release, session=self.session, protocol=protocol)
