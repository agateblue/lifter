=====
Usage
=====

Using lifter consists only of a few steps.

First of all, remember to import lifter in your project:

.. code-block:: python

    import lifter

Creating a model
----------------

This model will represent the data you are querying:

.. code-block:: python

    User = lifter.models.Model('User')
    # Or Dog, or Cat, or anything you want

Loading data into a manager
---------------------------

Managers are basically intermediate objects used to generate querysets.

.. code-block:: python

    manager = User.load(my_user_list)

Making queries
--------------

Once you have a manager set up, you can run an arbitrary number of queries on its data:

.. code-block:: python

    # Simple filters
    young_users = manager.filter(User.age < 30)
    old_users = manager.filter(User.age > 60)

    # Chained filters / excludes
    young_and_inactive_users = young_users.exclude(User.is_active == True)

    young_and_inactive_users.count()
    # >>> 45

    # Getting a single user
    kurt = manager.filter(User.email == 'kurt@cobain.com')

Queryset API
------------

Methods such as :py:func:`get`, :py:func:`filter` or :py:func:`exclude`, expect :py:class:`Query` objects as arguments,
and return a :py:class:`QuerySet` instance.

A :py:class:`Query` is basically a wrapper around a :py:class:`Path` (the attribute you are querying against),
and a test function:

.. code-block:: python

    # A path referring to the age attribute
    path = User.age

    # A query that will check the age attribute is greater than 36
    query = path > 36

    # You can use the query to match a single object if you want
    # Will return True if kurt.age > 36
    query.match(kurt)


QuerySet methods
****************

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


.. py:method:: exclude(*explicit_queries, **keyword_queries)

    This method is the exact opposite of  :py:func:`filter`. It will return
    objects that do *not* match the provided queries:

    .. code-block:: python

        # Exclude inactive users
        manager.exclude(User.is_active == False)

        # Exclude only inactive users that are 42 years-old
        manager.exclude(User.is_active == False, User.age == 42)

.. py:method:: get(*explicit_queries, **keyword_queries)

    This method retrieve a single object that match all of the given queries:

    .. code-block:: python

        kurt = manager.get(User.id == 447)

    Get will raise :py:class:`lifter.exceptions.DoesNotExist` if no object is found, and
    :py:class:`lifter.exceptions.MultipleObjectsReturned` if multiple objects are found:

    .. code-block::

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
******************

Some of the previously described methods allow chaining
You can chain querysets at will using :py:func:`filter` and/or :py:func:`exclude`:

.. code-block:: python

    manager.exclude(User.age == 34).filter(User.is_active == True).filter(User.has_beard == False)

The previous example tranlates to:

1. In all users, exclude then one where `age` equals 34
2. Then, from the previous queryset, keep only active users
3. Then, from the previous queryset, leave only users with no beard

Querysets are lazy
******************

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
