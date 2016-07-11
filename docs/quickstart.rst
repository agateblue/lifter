==========
Quickstart
==========

Using lifter consists only of a few steps.

Creating a model
----------------

This model will represent the data you are querying:

.. code-block:: python

    import lifter.models

    class User(lifter.models.Model):
        pass

Creating a data store
----------------------

In this example, we'll assume the data you want to query is available in the python process,
as an iterable. Therefore, we use the :doc:`Python store <backends/python>`:

.. code-block:: python

    from lifter.backends.python import IterableStore

    data = [
        {
            'age': 27,
            'is_active': False,
            'email': 'kurt@cobain.music',
        },
        {
            'age': 687,
            'is_active': True,
            'email': 'legolas@deepforest.org',
        },
        {
            'age': 34,
            'is_active': False,
            'email': 'golgoth@lahorde.org',
        }
    ]

    store = IterableStore(data)

In this step, we made our data available in lifter, so it can be queried later.

Creating a manager
------------------

Creating a manager is the next step:

.. code-block:: python

    manager = store.query(User)

With the previous line, we told lifter that our store will return ``User`` instances.

Your first query
----------------

Enough set up, let's run your first query:

.. code-block:: python

    young_users = manager.filter(User.age < 30)

The previous query will return a queryset containing all users matching ``age < 30``.

You could then iterate over those results and use them in your application:

.. code-block:: python

    for user in young_users:
        print('Hello {0}!'.format(user['email']))

More complex queries
--------------------

Of course, we just scratched the surface here. More complex and useful methods
are available in lifter:

.. code-block:: Python

    # get the total number of inactive users
    total_inactive = manager.filter(User.is_active == False).count()

    # get only legolas' data
    legolas = manager.get(User.email == 'legolas@deepforest.org')

    # get a list containing all users emails
    emails_list = manager.all().values_list('email', flat=True)

    # get total and average age of our users
    from lifter import aggregates

    manager.all().aggregate(
        aggregates.Sum('age'),
        aggregates.Avg('age'),
    )
    >>> {'age__avg': 249.33, 'age__sum': 748}

If you're interested, head over :doc:`Query API <query>`!
