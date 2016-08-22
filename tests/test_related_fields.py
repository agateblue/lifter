import unittest

from lifter import query, models, store, adapters
from lifter.backends import python
from lifter import aggregates
from lifter.backends.python import IterableStore


class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField()


class User(models.Model):
    group = models.ForeignKey(Group)


class DummyStore(python.DummyStore):
    def __init__(self, groups, users, **kwargs):
        self.groups = groups
        self.users = users
        super(DummyStore, self).__init__(**kwargs)

    def load(self, model, adapter):
        if model == User:
            source = [{'group': user.group.id} for user in self.users]
            return [adapter.parse(result, model, store=self) for result in source]
        if model == Group:
            return self.groups


class GroupAdapter(adapters.Adapter):
    pass


class UserAdapter(adapters.Adapter):
    group = adapters.DeferredForeignKey(GroupAdapter)


class TestRelatedFields(unittest.TestCase):

    def test_forkeign_key_return_deferred_resolver(self):
        group = Group(id=1, name='test')
        user = User(group=group)

        store = DummyStore(groups=[group], users=[user])
        u = store.query(User, adapter=UserAdapter()).first()
        self.assertEqual(u.group.id, group.id)
        self.assertTrue(u.group._deferred)

        self.assertEqual(u.group.name, 'test')
        self.assertEqual(u.group.id, 1)
        self.assertFalse(u.group._deferred)
