Django
=======

The :py:mod:`lifter.contrib.django` module provides integration of lifter's :doc:`Python backend </backends/python>`
on django's queryset. Once configured, you can apply additional filters and orderings to a django queryset
without extra calls to database.

It is compatible with django versions >= 1.7.

Installation
*************

You just need to add ``lifter.contrib.django`` to your installed apps:

.. code-block:: python

    INSTALLED_APPS = [
        # your other apps
        'lifter.contrib.django',
    ]

Internally, the application will monkey patch django's :py:class:`QuerySet`, by adding a single method.

Usage
******

Usage is really simple:

.. code-block:: python

    from django.contrib.auth import User

    # this is your regular django queryset
    all_users = User.objects.all()

    # we convert it to lifter Python's backend
    local_qs = all_users.locally()

    # the first query will evaluate the django's queryset (if needed),
    # triggering a database query
    local_qs.count()
    >>> 157

    # other queries are executed locally, on already loaded models,
    # so no database query will be thrown
    for user in local_qs.exclude(username='bob').order_by('-username'):
        print(user)

Of course, you can any method or lookup that is supported by lifter's Python backend.
