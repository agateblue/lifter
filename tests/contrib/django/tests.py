import unittest

import django
from django.test import TestCase

from lifter import query

class DjangoTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        from django.test.utils import setup_test_environment
        from django.core.management import call_command

        from django.conf import settings
        settings.configure(
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'lifter.contrib.django',
            ],
            DATABASES={
                'default': {'NAME': ':memory:', 'ENGINE': 'django.db.backends.sqlite3'}
            },
        )
        django.setup()
        setup_test_environment()
        super(DjangoTestCase, cls).setUpClass()

        call_command('migrate')

    def test_can_run_queryset_locally(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = [User.objects.create(username=str(i)) for i in range(10)]

        qs = User.objects.all()
        self.assertEqual(qs.count(), 10)

        local_qs = qs.locally().all()

        self.assertTrue(isinstance(local_qs, query.QuerySet))
        self.assertEqual(local_qs.count(), 10)

        with self.assertNumQueries(0):
            self.assertEqual(local_qs.count(), 10)
            self.assertEqual(local_qs.filter(username='1').count(), 1)
            
            for user in local_qs.order_by('-username'):
                pass
