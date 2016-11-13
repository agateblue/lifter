import unittest
from lifter import models


class TModel(models.Model):
    field = models.CharField()

    def __repr__(self):
        return 'test'

class TestMeta(unittest.TestCase):

    def test__meta_attribute_is_available_on_model(self):
        meta = TModel._meta
        self.assertTrue(isinstance(meta, models.Meta))

    def test__meta_attribute_has_model_fields_on_it(self):
        f = TModel._meta.fields['field']
        self.assertTrue(isinstance(f, models.CharField))

    def test_can_override_repr_on_model(self):
        m = TModel()
        self.assertEqual(repr(m), 'test')
