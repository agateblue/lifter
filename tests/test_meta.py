import unittest
from lifter import models


class TestModel(models.Model):
    field = models.CharField()

class TestMeta(unittest.TestCase):

    def test__meta_attribute_is_available_on_model(self):
        meta = TestModel._meta
        self.assertTrue(isinstance(meta, models.Meta))

    def test__meta_attribute_has_model_fields_on_it(self):
        f = TestModel._meta.fields['field']
        self.assertTrue(isinstance(f, models.CharField))
