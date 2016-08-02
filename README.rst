===============================
What is lifter?
===============================

.. image:: https://img.shields.io/pypi/v/lifter.svg
        :target: https://pypi.python.org/pypi/lifter

.. image:: https://readthedocs.org/projects/lifter/badge/?version=latest
        :target: http://lifter.readthedocs.org/en/latest/?badge=latest

.. image:: https://travis-ci.org/EliotBerriot/lifter.svg?branch=master
    :target: https://travis-ci.org/EliotBerriot/lifter

.. image:: https://travis-ci.org/EliotBerriot/lifter.svg?branch=develop
    :target: https://travis-ci.org/EliotBerriot/lifter


Lifter is a generic query engine, inspired by Django ORM and SQLAlchemy.

Its goal is to provide a unique interface to query any type of data, regardless of the underlying query language or data backend (SQL, REST, Python objects...).

**Warning**: This package is still in alpha state and a lot of work is still needed to make queries faster and efficient.
Contributions are welcome :)

Useful links:

- Documentation is available at http://lifter.readthedocs.org
- Ask your programming questions on Stack Overflow using the tag `python-lifter <http://stackoverflow.com/questions/tagged/python-lifter>`_

Features
--------

* Queryset API similar to Django_  and SQLAlchemy_
* Lazy querysets
* Composable queries
* Lightweight: very little dependencies
* Tested and working on Python 2.7 to Python 3.5

.. _Django: https://docs.djangoproject.com/en/1.9/ref/models/querysets/
.. _SQLAlchemy: http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html#common-filter-operators

Example usage
-------------

Consider the following list of users, returned from a REST API endpoint:

.. code-block:: python

    users = [
        {
            "is_active": True,
            "age": 35,
            "eye_color": "brown",
            "name": "Bernard",
            "gender": "male",
            "email": "bernard@blackbooks.com",
        },
        {
            "is_active": True,
            "age": 34,
            "eye_color": "brown",
            "name": "Manny",
            "gender": "male",
            "email": "manny@blackbooks.com",
        },
        {
            "is_active": True,
            "age": 35,
            "eye_color": "brown",
            "name": "Fran",
            "gender": "female",
            "email": "fran@blackbooks.com",
        },
        # And so on ...
    ]

Now, imagine you have to extract data from this list. Let's compare how you can do this using regular Python
and lifter.

To use lifter in your project, you'll only need the following instructions:

.. code-block:: python

    import lifter.models
    from lifter.backends.python import IterableStore

    class User(lifter.models.Model):
        pass

    store = IterableStore(users)
    manager = store.query(User)

Getting all active 26 years old users:

.. code-block:: python

    # vanilla Python
    results = [
        user for user in users
        if user['age'] == 26 and user['is_active']
    ]

    # lifter
    results = manager.filter(User.age == 26, User.is_active == True)

Getting names and emails of inactive users under 56:

.. code-block:: python

    # vanilla Python
    results = [
        (user['name'], user['email']) for user in users
        if not user['is_active'] and user['age'] < 56
    ]

    # lifter
    results = manager.filter(User.is_active == False, User.age < 56)\
                     .values_list('name', 'email')

Getting all active users except the one with brown eyes and sort them by age:

.. code-block:: python

    # vanilla Python
    raw_results = [
        user for user in users
        if user['is_active'] and not user['eye_color'] == 'brown'
    ]
    results = sorted(raw_results, key=lambda v: v['age'])

    # lifter
    results = manager.filter(User.is_active == True)\
                     .exclude(User.eye_color == 'brown')\
                     .order_by('age')

Getting minimum and average women age:

.. code-block:: python

    # vanilla Python
    from statistics import mean # Only in Python >=3.4
    women_ages = [
        user['age'] for user in users
        if user['gender'] == 'female'
    ]
    women_average_age = mean(women_ages)
    minimum_woman_age = min(women_ages)

    # lifter
    results = manager.filter(User.gender == 'female')\
                     .aggregate((User.age, mean), (User.age, min))

As you can see, lifter's version is shorter and more readable than vanilla Python.
It's also less error prone, especially if you're writing really complex queries,
and quite familiar if you've already used an ORM.

Wanna know more? Have a look at the documentation_!

.. _documentation: http://lifter.readthedocs.org
