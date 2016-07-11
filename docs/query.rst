Query API
==========

At the moment, lifter is read-only, meaning no write query can be issued to a store.

:py:class:`QuerySet` is the class used for read-related queries.

Paths
*****

``Paths`` refers to the fields of a model involved in a query. For example, take the following queryset:

.. code-block:: python

    class User(lifter.models.Model):
        pass

    manager.filter(User.age > 13, User.is_active == True)

In the previous example, two paths are used in the query: ``User.age`` and ``User.is_active``.

Thanks to a little magic, these paths are actually represented as plain python objects:

.. code-block:: python

    User.age
    >>> <Path: age>

Paths can actually be nested. If you have the following data source:

.. code-block:: python

    users = [
        {
            'id': 1,
            'name': 'Jeff Winger',
            'company': {
                'id': 3,
                'name': 'Greendale',
            }
        }
    ]

You can totally create paths such as ``User.company.id`` or ``User.company.name``.

Query nodes
************

Paths are used to create query nodes. A :py:class:`QueryNode` is a Python object, used to represent a condition:

.. code-block:: python

    path = User.age
    qn = path < 30

Of course, in real life, you'll use the shorter (and also more readable notation):

.. code-block:: python

    User.age < 30
    >>> <QueryNode age, <built-in function lt>, [30], {}>

In the previous example, we have created a query node representing the condition ``age < 30``.
We can now use this node to fetch data:

.. code-block:: python

    qn = User.age < 30
    manager.all().filter(qn)
    >>> Returns all user matching the condition

Combining nodes
----------------

It is possible to combine nodes together using python bitwise operators to build more complex queries:

.. code-block:: python

    qn = (User.age < 30) & (User.is_active == True)
    >>> a node matching User.age < 30 AND User.is_active == True

    qn = (User.age < 30) | (User.is_active == True)
    >>> a node matching User.age < 30 OR User.is_active == True

    # use ~ to invert a query node
    qn = ~(User.age < 30)

Queries
********

Queries are higher-level objects that describe an action to run on the data store:

.. code-block:: python

    import lifter.query

    qn = (User.age < 30) & (User.is_active == False)
    query = lifter.query.Query(action='select', filters=qn)


QuerySets
**********

Don't worry, you won't have to instanciate all of these objects by hand to use lifter.

QuerySets are here to provide the high-level API for interacting with data stores.

Once you have a manager instance, issuing query is done easily with querysets:

.. code-block:: python

    import lifter.models
    from lifter.backends.python import IterableStore

    class User(lifter.models.Model):
        pass

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
    manager = store.query(User)

    # Here you pass query nodes directly to the queryset to obtain results from the store
    manager.filter(User.age < 30)

QuerySet methods
----------------

.. py:method:: filter(*explicit_queries, **keyword_queries)

    Return a set of objects that match one or multiple queries.

    Simple example using one query:

    .. code-block:: python

        # return all 42 years-old users
        manager.filter(User.age == 42)

    Providing multiple queries to this method will merge all of them using AND operator:

    .. code-block:: python

        manager.filter(User.age >= 42, User.age <= 56)

    The previous example will return only objects that match *both* queries.

    This is equivalent of writing:

    .. code-block:: python

        manager.filter((User.age >= 42) & (User.age <= 56))

.. py:method:: exclude(*explicit_queries, **keyword_queries)

    This method is the exact opposite of :py:func:`filter`. It will return
    objects that do *not* match the provided queries:

    .. code-block:: python

        # Exclude inactive users
        manager.exclude(User.is_active == False)

        # Exclude only inactive users that are 42 years-old
        manager.exclude(User.is_active == False, User.age == 42)

    Providing multiple queries to this method will merge all of them using AND operator:

    This is equivalent of writing:

    .. code-block:: python

        manager.exclude((User.age >= 42) & (User.age <= 56))

.. py:method:: get(*explicit_queries, **keyword_queries)

    This method retrieve a single object that match all of the given queries:

    .. code-block:: python

        kurt = manager.get(User.id == 447)

    Get will raise :py:class:`lifter.exceptions.DoesNotExist` if no object is found, and
    :py:class:`lifter.exceptions.MultipleObjectsReturned` if multiple objects are found:

    .. code-block:: python

        import lifter.exceptions

        try:
            kurt = manager.get(User.first_name == 'Kurt')
        except lifter.exceptions.DoesNotExist:
            print('Sorry, no user found, try something else')
        except lifter.exceptions.MultipleObjectsReturned:
            print('Multiple users are named Kurt, please precise your query')

    This method will retrieve the final object among the queryset values:

        >>> manager.get(User.first_name == 'Kurt')
        # Retrieve among all manager loaded objects
        >>> manager.filter(User.age == 42).get(User.first_name == 'Kurt')
        # Retrieve among 42 years-old users

.. py:method:: order_by(*paths)

    Order the queryset results using the provided attribute(s):

    .. code-block:: python

        >>> manager.order_by(User.age)
        # Returns a queryset of users, from younger to older

    You can reverse the ordering using python invert operator:

    .. code-block:: python

        >>> manager.order_by(~User.age)
        # Returns a queryset of users, from older to younger, this time

    It's possible to sort using multiple paths:

    .. code-block:: python

        >>> manager.order_by(User.is_active, User.age)
        # Sort by is_active then by age

    Finally, you can also use random sorting, by passing a question mark instead of a path:

    .. code-block:: python

        >>> manager.order_by('?')
        # Random order
        >>> manager.order_by(User.age, '?')
        # Sort by age then randomly

.. py:method:: values(*paths)

    Use this method if you only want to retrieve specific values from your object list,
    instead of the objects themselves. It will return a list of dictionaries, with the requested values
    as keys:

    .. code-block:: python

        >>> manager.values(User.age, User.email)
        [{'age': 36, 'email': 'benard@blackbooks.com'}, {'age': 33, 'email': 'manny@blackbooks.com'}]

.. py:method:: values_list(*paths, flat=False)

    This method works as :py:func:`values`, but instead of of list of dictionaries, it returns
    a list of tuples.

    .. code-block:: python

        >>> manager.values_list(User.age, User.email)
        [(36, 'benard@blackbooks.com'), (33, 'manny@blackbooks.com')]

    If you're only requesting a single value and want a flat list (no tuples in it),
    you can set the `flat` parameter to True:

    .. code-block:: python

        >>> manager.values_list(User.email, flat=True)
        ['benard@blackbooks.com', 'manny@blackbooks.com']

.. py:method:: count()

    A helper method that return the number of objects inside the queryset:

    .. code-block:: python

        >>> manager.filter(User.age == 42).count()
        56

    You can achieve the same result using `len`:

    .. code-block:: python

        qs = manager.filter(User.age == 42)
        print(len(qs))

.. py:method:: first()

    A helper method that return the first object of the queryset or `None` if it's empty:

    .. code-block:: python

        >>> manager.filter(User.age == 42).first()
        <User object>
        >>> manager.filter(User.age == 666).first()
        None

.. py:method:: last()

    Works as :py:func:`first` but returns the last object of the queryset.

.. py:method:: exists()

    A helper method that return `True` if the queryset has at least one result, `False` otherwise:

    .. code-block:: python

        >>> manager.filter(User.age == 666).exists()
        False

.. py:method:: distinct()

    A method that remove duplicates from a queryset:

    .. code-block:: python

        >>> manager.values_list(User.eye_color, flat=True)
        ['green', 'brown', 'green', 'red', 'brown', 'red']
        >>> manager.values_list(User.eye_color, flat=True).distinct()
        ['green', 'brown', 'red']

.. py:method:: aggregate(*aggregates, **named_aggregates, flat=False)

    Extract data from the queryset objects and return it as a dictionary.

    A simple example to retrieve the average age of all users:

    .. code-block:: python

        >>> import statistics
        >>> manager.aggregate((User.age, statistics.mean))
        {'age__mean': 44.2}

    Under the hood, the previous example will loop on all loaded users, grab the `age` attribute,
    append the age to a list, then pass this list to the `mean` function and return the final result.

    The method expect `(path, callable)` tuples as parameters. The path is the object attribute
    you want to gather, and the callable is the function that will return a value from the gathered data.

    You can request multiple aggregates at once:

    .. code-block:: python

        >>> manager.aggregate((User.age, statistics.mean), (User.age, min))
        {'age__mean': 44.2, 'age__min': 12}

    Bind them to specific keys:

    .. code-block:: python

        >>> manager.aggregate(average_age=(User.age, statistics.mean))
        {'average_age': 44.2}

    And return aggregates as a list instead of a dictionary using the `flat` parameter:

    .. code-block:: python

        >>> manager.aggregate((User.age, statistics.mean), (User.age, min), flat=True)
        [44.2, 12]

Chaining querysets
-------------------

Some of the previously described methods allow chaining
You can chain querysets at will using :py:func:`filter` and/or :py:func:`exclude`:

.. code-block:: python

    manager.exclude(User.age == 34).filter(User.is_active == True).filter(User.has_beard == False)

The previous example tranlates to:

1. In all users, exclude then one where `age` equals 34
2. Then, from the previous queryset, keep only active users
3. Then, from the previous queryset, leave only users with no beard

Querysets are lazy
--------------------

No matter how much time you chain :py:func:`filter` and/or :py:func:`exclude` calls,
the final query will only be actually applied when you try to access the queryset data:

.. code-block:: python

    # This will be instant, even if your user list has 1,000,000,000 entries in it
    queryset = manager.exclude(User.age == 16)

    # however, calling one of the following will apply the filter
    queryset.count()
    for user in queryset:
        print(user.age)

Once a queryset is evaluated (when queries have been applied), results are stored internally,
and the queryset can be looped has many times as you want at no cost.
