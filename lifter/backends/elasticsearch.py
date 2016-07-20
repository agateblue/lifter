import operator
from . import http
from .. import adapters
from .. import store


class ES2RefinedStore(http.RESTRefinedStore):
    pluralize_model_name = False

    def get_out_attribute_names_converter(self):
        return lambda v: v

    def get_default_adapter(self):
        return adapters.DictAdapter(recursive=True, key='_source')

    def get_querystring_builder(self, query):
        return ES2QueryStringBuilder()

    def build_query_url(self, query):
        base = super(ES2RefinedStore, self).build_query_url(query)

        if query.action == 'select':
            end = '_search'
        if query.action == 'count':
            end = '_count'

        return base + '/' + end

    def get_results(self, data, query):
        if query.action == 'select':
            return data['hits']['hits']
        return data

    def build_querystring(self, query):
        qs = super(ES2RefinedStore, self).build_querystring(query)
        if query.window:
            qs['size'] = query.window.size
            qs['from'] = query.window.start_as_int

        subsets = [str(path) for path in query.hints.get('paths', [])]
        if subsets:
            qs['_source'] = ','.join(subsets)

        return qs

    def handle_count(self, query):
        url = self.build_query_url(query)
        request = self.build_request(url, query)
        response = self.get_response(request)
        parsed_response = self.parse_response(response)
        return parsed_response['count']

    @store.cast_to_values
    def handle_values(self, query):
        return self.handle_select(query.clone(action='select'))


class ES2Store(http.RESTStore):
    refined_class = ES2RefinedStore


def _get_eq(lookup):
    op = ''
    if isinstance(lookup.reference_value, str):
        return op, '"{0}"'.format(lookup.reference_value)
    return op, lookup.reference_value

class ES2QueryStringBuilder(http.QueryStringBuilder):
    """
    Compile query filters to ES2 required format
    """

    support_table = {
        'lookups': [
            'eq',
            'gt',
            'gte',
            'lt',
            'lte',
        ],
        'operators': [
            'AND',
            'NOT',
            'OR',
        ]
    }

    lookups_mapping = {
        'eq': _get_eq,
        'gt': lambda lookup: ('>', lookup.reference_value),
        'gte': lambda lookup: ('>=', lookup.reference_value),
        'lt': lambda lookup: ('<', lookup.reference_value),
        'lte': lambda lookup: ('<=', lookup.reference_value),

    }

    def get_filters_as_dict(self, node):
        d = {}

        d['q'] = self.get_query_as_str(node)
        return d

    def get_orderings_as_dict(self, orderings):
        o = []
        for ordering in orderings:
            direction = 'desc' if ordering.reverse else 'asc'
            o.append('{0}:{1}'.format(ordering.path, direction))

        return {
            'sort': ','.join(o)
        }

    def cast_test(self, node):
        return self.lookups_mapping[node.lookup.registry_name](node.lookup)

    def get_query_as_str(self, node):
        self.check_support(node)

        try:
            subqueries = []
            for sq in node.subqueries:
                subqueries.append(self.get_query_as_str(sq))
            q = '(' + ' {0} '.format(node.operator).join(subqueries) + ')'

        except AttributeError:
            # Leaf query
            test, value = self.cast_test(node)
            q = '{0}:{1}{2}'.format(node.path, test, value)

        if node.inverted:
            q = 'NOT {0}'.format(q)
        return q
