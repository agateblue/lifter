import operator
import requests

from .. import __version__
from .. import store
from .. import parsers
from .. import exceptions
from .. import utils

class RESTRefinedStore(store.RefinedStore):
    pluralize_model_name = True

    def get_out_attribute_names_converter(self):
        return utils.to_camel_case

    def convert_attribute_names_out(self, querystring):
        converter = self.get_out_attribute_names_converter()
        return {
            converter(key): value
            for key, value in querystring.items()
        }

    def get_user_agent(self):
        return 'Lifter/{0}'.format(__version__)

    def get_headers(self, query):
        return {
            'User-Agent': self.get_user_agent(),
        }

    def build_request(self, url, query):
        method = 'GET'
        headers = self.get_headers(query)
        querystring = self.build_querystring(query)
        querystring = self.convert_attribute_names_out(querystring)
        request = requests.Request(method, url, params=querystring, headers=headers).prepare()

        return request

    def get_model_url_part(self):
        app_part = self.model._meta.app_name
        if self.pluralize_model_name:
            model_part = self.model._meta.name_plural
        else:
            model_part = self.model._meta.name
        if app_part:
            return app_part + '/' + model_part
        return model_part

    def build_query_url(self, query):
        model_part = self.get_model_url_part()
        if self.parent.base_url.endswith('/'):
            resource_url = self.parent.base_url + model_part
        else:
            resource_url = self.parent.base_url + '/' + model_part

        return resource_url

    def get_querystring_builder(self, query):
        return SimpleQueryStringBuilder()

    def build_querystring(self, query):
        qs = {}
        if query.filters:
            builder = self.get_querystring_builder(query)
            qs.update(builder.build(query.filters, orderings=query.orderings))
        return qs

    def get_response(self, request):
        return self.parent.session.send(request)

    def parse_response(self, response):
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code >= 400 and response.status_code < 500:
                raise exceptions.BadQuery(str(e))
            if response.status_code >= 500:
                raise exceptions.StoreError(str(e))
        parser = self.get_parser(response)
        return parser.parse(response.content.decode('utf-8'))

    def get_parser(self, response):
        # if response.headers['Content-Type'] in ['application/javascript', 'application/json']:
        return parsers.JSONParser()

    def get_results(self, data, query):
        return data

    @store.cast_results_to_model
    def handle_select(self, query):
        url = self.build_query_url(query)
        request = self.build_request(url, query)
        response = self.get_response(request)
        parsed_response = self.parse_response(response)
        return self.get_results(parsed_response, query)

    def handle_count(self, query):
        query = query.clone(action='select')
        return len(self.handle_select(query))

class RESTStore(store.Store):

    refined_class = RESTRefinedStore

    def __init__(self, *args, **kwargs):
        self._session = kwargs.pop('session', None) or requests.Session()
        self.base_url = kwargs['base_url']
        super(RESTStore, self).__init__()

    @property
    def session(self):
        return self._session


class QueryStringBuilder(object):
    """
    Will build the correct querystring from a given query node
    """

    def check_support(self, node):
        if node.inverted and 'NOT' not in self.support_table['operators']:
            raise exceptions.UnsupportedQuery('NOT operator not supported', query=node)

        if hasattr(node, 'test') and node.test not in self.support_table['tests']:
            raise exceptions.UnsupportedQuery('{0} test not supported'.format(node.test), query=node)

        if hasattr(node, 'operator') and node.operator not in self.support_table['operators']:
            raise exceptions.UnsupportedQuery('{0} operator not supported'.format(node.operator), query=node)

    def get_filters_as_dict(self, node):
        raise NotImplementedError()

    def build(self, node=None, orderings=None):
        r = {}
        if node:
            r.update(self.get_filters_as_dict(node))
        if orderings:
            r.update(self.get_orderings_as_dict(orderings))
        return r

class SimpleQueryStringBuilder(QueryStringBuilder):

    support_table = {
        'tests': [
            operator.eq,
        ],
        'operators': [
            'AND',
        ]
    }

    def get_filters_as_dict(self, node):
        d = {}

        for key, value in self.iterate(node):
            l = d.setdefault(key, [])
            l.append(value)

        return d

    def iterate(self, node):
        self.check_support(node)
        try:
            for sq in node.subqueries:
                for r in self.iterate(sq):
                    yield r
        except AttributeError:
            # Leaf query
            yield str(node.path), node.test_args[0]
