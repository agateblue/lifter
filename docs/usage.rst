
Installation
------------

At the command line::

    $ pip install lifter

Usage
-----

To use lifter in a project:

.. code-block:: python

    import lifter

Before running queries, you need to load your data inside a manager:

.. code-block:: python

    manager = lifter.load(my_iterable)

If you want to use the same data as the examples provided in this documentation,
copy-paste the content of `tests/fake_data.py` inside your python interpreter then run:

.. code-block:: python

    manager = lifter.load(fake)

.. note::

    All examples use a list of dictionaries as source data, but lifter works exactly the same
    if you feed your manager with a list of regular objects. Lifter will seamlessly lookup both object attributes and
    dictionary keys.

About querysets
+++++++++++++++

Just like Django, lifter is based on querysets_. Basically, a queryset in lifter is an object containing values
with functions to refine these values.

You can chain most queryset methods, which wil give you enough flexibility to build complex queries:

.. code-block:: python

    results = manager.all().filter(is_active=True).exclude(age=42).order_by('age')

    for result in results:
        # do something with the results

.. note::

   Unless stated otherwise, all queryset methods behave just like Django querysets_

.. warning::

    At the moment, lifter querysets are not lazy, which mean they are applied immediately when called.

filter
++++++

One of the most basic query method is `filter`. Use it if you want to retrieve objects that match a set of criteria. Example:

.. code-block:: python

    manager.filter(name='Manny')

The previous example will return a `QuerySet` instance containing all users whose name equals `Manny`.
It's absolutely okay to provide multiple arguments at once:

.. code-block:: python

    # these two queries have the same effect
    manager.filter(name='Manny', has_beard=True)
    manager.filter(name='Manny').filter(has_beard=True)

This time, we'll only get users named `Manny` AND with a beard.

get
+++

`get` returns a single object that match a set of criteria, raising an exception if no value is found or if multiple values are found:

.. code-block:: python

    manager.get(name='Fran', gender='female')

You can catch these exceptions as follow:

.. code-block:: python

    try:
        manager.get(name='Hodor')
    except lifter.DoesNotExist:
        print('Wrong show dude')

    try:
        manager.get(gender='male')
    except lifter.MultipleObjectsReturned:
        print('Bernard or Manny, you have to choose')

And, finally, you can chain `get` after other querysets to reduce available choices:

.. code-block:: python

    # the following will look for a single male among users without beard
    manager.filter(has_beard=False).get(gender='male')

exclude
+++++++

This method is the exact opposite of `filter`. Use it if you want to retrieve objects that do not match a set of criteria. Example:

.. code-block:: python

    manager.exclude(name='Bernard')

The previous example will return a `QuerySet` instance containing all users not named `Bernard`.
Contrary to `filter`, providing multiple arguments at once and chaining do not achieve the same thing:

.. code-block:: python

    # This will exclude only objects with name == 'Bernard' AND own_bookshop == True
    manager.exclude(name='Bernard', own_bookshop=True)

    # This will exclude objects with name == 'Bernard' OR own_bookshop == True
    manager.exclude(name='Bernard').exclude(own_bookshop=True)

order_by
++++++++

.. note::

    By default, order of provided data is preserved accross all subsequent querysets,
    unless you explicitly call `order_by` at some point.

Use this method to change results' order based on a given attribute:

.. code-block:: python

    # will return younger users first
    manager.all().order_by('age')

You can prefix the attribute with `-` to reverse the ordering:

.. code-block:: python

    # will return older users first
    manager.all().order_by('-age')

.. code-block:: python

    # will return random ordered queryset
    manager.all().order_by('?')

count
+++++

A simple method that returns the number of object inside the queryset:

.. code-block:: python

    manager.filter(has_beard=False).count()

exists
++++++

A simple method that return `True` if a queryset contains at least one result, returning `False` otherwise:

.. code-block:: python

    # return True
    manager.filter(has_beard=False).exists()

first
+++++

A shortcut that returns the first result or `None` if the query has no results:

.. code-block:: python

    manager.all().first()

last
++++

Same as `first`, but return the last result.

values
++++++

Use `values` if you don't want to access original objects but only a subset of specific values:

.. code-block:: python

    # will return a list of dictionaries as follow:
    # [
    #     {'name': 'Bernard', 'email': 'bernard@blackbooks.com'},
    #     {'name': 'Manny', 'email': 'manny@blackbooks.com'},
    # ]
    manager.all().values('name', 'email')

values_list
+++++++++++

This method behaves as `values`, but return a list of tuples instead of a list of dictionaries:

.. code-block:: python

    # will return a list of tuples as follow:
    # [
    #     ('Bernard', 'bernard@blackbooks.com')
    #     ('Manny', 'manny@blackbooks.com')
    # ]
    manager.all().values_list('name', 'email')

Additionaly, if you only want a single value without nested tuples, you can provide the optional `flat` parameter:

.. code-block:: python

    # will return a list as follow:
    # ['Bernard', 'Manny']
    manager.all().values_list('name', flat=True)

distinct
++++++++

`distinct` remove duplicate entries in a queryset:

.. code-block:: python

    # will return ['blue', 'brown', 'green', 'purple']
    manager.order_by('eye_color').values_list('eye_color', flat=True).distinct()

Spanning lookups
++++++++++++++++

If you want to access attributes from nested objects, you can use the following lookup syntax:

.. code-block:: python

    # will filter users with a company whose name is "blackbooks"
    manager.filter(company__name='blackbooks')

    # return a list of all companies names, without duplicates
    manager.values_list('company__name', flat=True).distinct()

Complex lookups
+++++++++++++++

Most of the time, simple lookups using equality in `filter`/`exclude` clauses will be enough. If it's not the case, you can
user built-in lookups to build more complex queries:

.. code-block:: python

    # return all users older than 37
    manager.filter(age=lifter.gt(37))

    # exclude all users under 43
    manager.exclude(age=lifter.lt(43))

    # return all users between 21 and 27 years old
    manager.exclude(age=lifter.value_range(21, 27))

    # return users with brown or green eyes
    manager.filter(eye_color=lifter.value_in(['brown', 'green']))

Finally, if you need a lookup that is not provided, you can provide a callable to `filter` and `exclude`:

.. code-block:: python

    # Leave only users whose age is odd
    manager.exclude(age=lambda v: v % 2 == 0)

Note that such callables **must** return a boolean.

Available lookups:

- `gt`: greater than
- `gte`: greater than or equal
- `lt`: less than
- `lte`: less than or equal
- `startswith`: case sensitive startswith
- `istartswith`: case insensitive startswith
- `endswith`: case sensitive endswith
- `iendswith`: case insensitive endswith
- `contains`: case sensitive search
- `icontains`: case insensitive search
- `value_in`: value is present in given iterable
- `value_range`: value is between given range

Aggregation
+++++++++++

If you want to extract global data instead of returning results, you can use aggregation:

.. code-block:: python

    # return the total number of children of all users combined, like this:
    # {'number_of_children__sum': 267}

    manager.all().aggregate(lifter.Sum('number_of_children'))

You can bind the aggregate to a custom key:

.. code-block:: python

    # {'children': 267}
    manager.all().aggregate(children=lifter.Sum('number_of_children'))

Additionaly, you can return multiple aggregates at once:

.. code-block:: python

    manager.all().aggregate(lifter.Sum('number_of_children'), lifter.Avg('age'))

If you would rather have a flat list of values returned, use the flat keyword:

.. code-block:: python

    # [267]

    manager.all().aggregate(children=lifter.Sum('number_of_children'), flat=True)

Available lookups are:

- `Sum`: sums the values of the given field
- `Min`: return the lowest value
- `Max`: return the greatest value
- `Avg`: return the average value
