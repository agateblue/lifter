Python backend
===============


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
