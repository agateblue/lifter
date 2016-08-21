import json
import xml.etree.ElementTree as ET


class Parser(object):
    def parse(self, content):
        raise NotImplementedError()


class JSONParser(Parser):
    def parse(self, content):
        return json.loads(content)


class XMLParser(Parser):
    results = './*'
    ns = {}

    def __init__(self, *args, **kwargs):
        # The xpath expression to use to filter results
        self.results = kwargs.pop('results', self.results)
        
        self.ns = kwargs.pop('ns', self.ns)
        super(XMLParser, self).__init__(*args, **kwargs)

    def parse(self, content):
        parsed = ET.fromstring(content)
        results = parsed.findall(self.results, self.ns)

        return results
