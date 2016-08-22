import unittest
import xml.etree.ElementTree as ET
import os


from lifter import parsers, models, utils, adapters

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'bucket.xml')


class StaticFile(models.Model):
    pass


class Adapter(adapters.ETreeAdapter):
    pass


class TestETreeAdapter(unittest.TestCase):
    def setUp(self):
        with open(DATA_PATH) as f:
            content = f.read()
        self.ns = {
            'amazon': 'http://s3.amazonaws.com/doc/2006-03-01/'
        }
        parser = parsers.XMLParser(
            results='./amazon:Contents',
            ns=self.ns,
        )
        self.results = parser.parse(content)

    def test_fields_are_collected_on_adapter_meta(self):
        fields = {
            'username': adapters.Field('nom_utilisateur'),
            'age': adapters.Field(),
        }

        class A(adapters.Adapter):
            username = fields['username']
            age = fields['age']

        a = A()
        self.assertEqual(a._meta.fields['age'], fields['age'])
        self.assertEqual(a._meta.fields['username'], fields['username'])

    def test_etree_adapter(self):
        self.assertEqual(len(self.results), 8)

        adapter = adapters.ETreeAdapter()
        for r in self.results:
            static_file = adapter.parse(r, StaticFile, store=None)
            for e in r:
                name = utils.to_snake_case(adapter.tag_to_field_name(e.tag))
                v = getattr(static_file, name)

                self.assertEqual(v, e.text)
