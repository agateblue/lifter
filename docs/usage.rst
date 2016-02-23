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

When you create a :py:class:`QuerySet` by calling one of the previous methods, lifter will store the query,
and apply it when it's time to actually retrieve the data (usually when you loop over the results).

Chaining querysets
******************

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
