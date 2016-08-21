
import random
import sys
import unittest
import mock

import lifter.models
import lifter.aggregates
import lifter.exceptions
import lifter.lookups
from lifter.backends.python import IterableStore


class TestObject(object):
    def __init__(self, name, **kwargs):
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return self.name

class TestBase(unittest.TestCase):
    PARENTS = [
        TestObject(name='parent_1'),
        TestObject(name='parent_2'),
    ]
    OBJECTS = [
        TestObject(name='test_1', order=2, a=1, parent=PARENTS[0], label='alabama', surname='Mister T'),
        TestObject(name='test_2', order=3, a=1, parent=PARENTS[0], label='arkansas', surname='Colonel'),
        TestObject(name='test_3', order=1, a=2, parent=PARENTS[1], label='texas', surname='Lincoln'),
        TestObject(name='test_4', order=4, a=2, parent=PARENTS[1], label='washington', surname='clint'),
    ]

    DICTS = [o.__dict__ for o in OBJECTS]

    def setUp(self):
        self.manager = IterableStore(self.OBJECTS).query(TestModel)
        self.dict_manager = IterableStore(self.DICTS).query(TestModel)


class TestModel(lifter.models.Model):
    pass


class TestQueries(TestBase):
    def test_querying_missing_field_raises_exception(self):
        manager = IterableStore(self.OBJECTS).query(TestModel)
        qs = manager.filter(nope='something')
        with self.assertRaises(lifter.exceptions.MissingField):
            list(qs)

    def test_querying_missing_field_silent_exception_when_permissive(self):
        manager = IterableStore(self.OBJECTS).query(TestModel)
        qs = manager.filter(nope='something').hints(permissive=True)
        list(qs)
