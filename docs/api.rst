API
========

In this document, we'll explain more deeply how lifter is designed and how each part interact with other ones.

Lifter's main goal is to provide a :doc:`generic query API  <query>` that can handle any data source.

Programming is always easier when you focus on data. So we'll start by explaining how models works.

.. currentmodule:: lifter.models

The :py:class:`Model`
**********************

In lifter, the :py:class:`Model` class is a place safe from the outside world, representing
how our data is structured.

Here is an example model:

.. code-block:: python

    from lifter import models

    class User(models.Model):
        id = models.IntegerField(primary_key=True)
        age = models.IntegerField()
        date_joined = models.DateField()

        @property
        def is_adult(self):
            return self.age >= 21

What we say here is we have a resource called ``User``.

Each user has:

- An ``id`` (which is a unique integer)
- An ``age`` (which is an integer)
- A ``date_joined`` attribute representing the registration date on our services

We don't care if the ``User`` data is stored in a SQL database, a REST API, a JSON file or any
other backend. Instead, we describe our ``User`` model behaviour, regardless of the data source.

Let's create our first user:

.. code-block:: python

    import datetime

    bob = User(id=1, age=21, date_joined=datetime.date(2016, 1, 12))
    bob.is_adult
    >>> True

.. currentmodule:: lifter.query

The :py:class:`Query`
*********************

Now, let's be honest: data must be stored somewhere. So we'll always need a way
to interact with it. This usually involves writing queries in another language, sending them to a data store,
parsing results and, finally, use these results in our application.

Of course, each data store has his own logic, structure, query language, meaning you cannot easily switch from one store
to another. If you decide to move your user data, previously stored in a SQL database, to a HTTP microservice, you'll probably have to
rewrite every single query in your application.

To better understand how it's possible, we'll start by explaining how queries are structured in lifter.

.. note::

    At the moment, the :py:class:`Query` object is still a work in progress.

You can easily create queries by hand in lifter:

.. code-block:: python

    from lifter import query

    filters = query.Path('age') == 18
    q = query.Query(action='select', filters=filters)

In the previous example, we created a simple query that express the following:

    Select everything where age == 18


.. currentmodule:: lifter.query

The :py:class:`Store`
*********************

Now, we have a query, but it is quite useless as is. To actually use it,
we would have to pass it to a store that is able to compile it.

For example, a HTTP store would compile it to a HTTP request at URL:

    /users/?age=18

While a SQL store would translate it to:

    SELECT * from users where age = 18;

A Python store would instead do:

.. code-block:: python

    filter(lambda user: user.age == 18, users)

And so on.

Hopefully, once executed, your compiled query will return results. It can be
a JSON or a XML payload, a bunch of SQL rows, or any structured format.

The store is also responsible for doing the initial parsing of such a payload.

Let's say our HTTP API endpoint returns the following JSON after the request to ``/users/?age=18``:

    {
        "status": "Ok",
        "count": 276,
        "results": [
            {
                "id": 12,
                "age": 18,
                "joinedDate": "2014-01-02",
            },
            {
                "id": 46,
                "age": 18,
                "joinedDate": "2015-02-04",
            },
            {
                "id": 77,
                "age": 18,
                "joinedDate": "2016-02-04",
            }
        ]
    }

The store will parse this response into a plain Python dictionary, and keep only the ``results`` key.

Then, to
