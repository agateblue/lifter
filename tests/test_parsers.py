import unittest
import xml.etree.ElementTree as ET

from lifter import parsers


class TestParsers(unittest.TestCase):

    def test_xml_parser(self):
        parser = parsers.XMLParser()
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <Results>
            <Result>
                <title>Hello</title>
            </Result>
            <Result>
                <title>World</title>
            </Result>
        </Results>
        """

        result = parser.parse(content)
        expected = ET.fromstring(content)

        for i, title in enumerate(['Hello', 'World']):
            self.assertEqual(result[i][0].text, title)
            self.assertEqual(expected[i][0].text, title)

    def test_xml_parser_can_use_xpath_to_retrieve_correct_results(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <Results>
            <Count>2</Count>
            <Result>
                <title>Hello</title>
            </Result>
            <Result>
                <title>World</title>
            </Result>
        </Results>
        """
        parser = parsers.XMLParser(results='./Result')
        result = parser.parse(content)
        for i, title in enumerate(['Hello', 'World']):
            r = result[i]
            self.assertEqual(r[0].text, title)

    def test_xml_parser_can_use_namespaces(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <Results xmlns:test="http://test.example.com">
            <Count>2</Count>
            <test:Result>
                <title>Hello</title>
            </test:Result>
            <test:Result>
                <title>World</title>
            </test:Result>
        </Results>
        """
        ns = {
            'test': 'http://test.example.com',
        }
        parser = parsers.XMLParser(results='./test:Result', ns=ns)
        result = parser.parse(content)
        for i, title in enumerate(['Hello', 'World']):
            r = result[i]
            self.assertEqual(r[0].text, title)
