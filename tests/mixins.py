import unittest
import json

class HTTPMixin(unittest.TestCase):

    def assertDictEqualsModel(self, d, m):
        for key, value in d.items():
            self.assertEqual(getattr(m, key), value)

    def mock_request(self, mock, url, data):
        headers = {
            'Content-Type': 'application/json; charset=UTF-8'
        }
        return mock.get(url, text=json.dumps(data), headers=headers)
