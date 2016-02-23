Overview
========

Lifter is a package that heavily inspires from `Django's ORM`_ in the way it works.
Some parts of the API are also quite similar to `TinyDB`_ and `SQLAlchemy`_.

.. _`Django's ORM`: https://docs.djangoproject.com/en/1.9/topics/db/queries/
.. _TinyDB: http://tinydb.readthedocs.org/en/latest/
.. _SQLAlchemy: http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html#common-filter-operators

Supported data structures
-------------------------

Lifter operates on collections of objects. A collection can be any Python iterable, like
a list, a tuple, or even a generator. As long as lifter can iterate on it, everythings fine.

Such collections must contain similarly structured objects in order for lifter to work:

.. code-block:: python

    # okay
    tags = [
        {'name': 'python', 'articles_count': 134},
        {'name': 'ruby', 'articles_count': 42},
        {'name': 'php', 'articles_count': 23},
    ]

    # okay
    class User(object):
        def __init__(self, age, first_name, last_name):
            self.age = age
            self.first_name = first_name
            self.last_name = last_name

    users = [
        User(42, 'Douglas', 'Adams'),
        User(867, 'Legolas', 'The Elf'),
        User(98, 'Benjamin', 'Button'),
    ]

    # not okay
    users_and_tags = [tags[0], users[0], tags[1], users[1]]

If your iterable contains mappings (such as dictionaries), lifter will treat them as regular objects,
and transparently access keys instead of attributes when filtering, retrieving and aggregating values.

Supported queries
-----------------

At the moment, lifter support two ways two make queries:

1. the explicit engine, which looks like SQLAlchemy. Example: `manager.filter(User.age == 42)`. **This is the recommended engine for any new project**
2. the keyword engine, which looks like Django. Example: `manager.filter(age=42)`. This is the engine that was built-in in the first release of the package.

Internally, lifter converts all queries to the explicit engine. This mean if you do `manager.filter(age=42)`,
lifter will convert it to `manager.filter(User.age == 42)`.

.. warning::

    We recommend using the explicit engine for any new projects involving lifter. The keyword engine will be kept
    for backward compatibility until and if a deprecation plan is adopted.
