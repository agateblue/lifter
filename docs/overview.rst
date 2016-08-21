Overview
========

Lifter is a package that heavily inspires from `Django's ORM`_ in the way it works.
Some parts of the API are also quite similar to `TinyDB`_ and `SQLAlchemy`_.

However, lifter intends to work with any data provider, meaning you can query data from various sources, using the same high-level API.

If implemented correctly, you can for exemple work on a project with static JSON data from a file during development, and easily switch to
a real REST API when it's time.

.. _`Django's ORM`: https://docs.djangoproject.com/en/1.9/topics/db/queries/
.. _TinyDB: http://tinydb.readthedocs.org/en/latest/
.. _SQLAlchemy: http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html#common-filter-operators

To achieve this, lifter tries to be as agnostic and flexible as possible regarding data sources, while adressing most common use cases.

The big picture
---------------

Lifter is made of several layers, each one fulfilling a specific task.

.. graphviz::

    digraph query {
        label="Journey of a query in lifter";
        labelloc="t";
        Manager -> Store;
        "Store" -> "Compiled query";
        "Compiled query" -> "Backend (SQL, REST...)";
        "Backend (SQL, REST...)" -> "Raw results";
        "Raw results" -> "Adapter";
        "Adapter" -> "Model instances";

    }

Models
******

Just like Django, lifter models are Python classes representing your data. You could have a ``User`` model and a ``Group`` model.

Stores
******

Stores are responsible for parsing queries about a model, send them to an underlying backend and return proper results
to lifter.

Adapters
********

Because we don't want to deal with raw data such as SQL or JSON Responses, adapters are reponsible for converting
data returned by our refined stores to actual model instances.

Managers
*********

Managers are the main entrypoint in lifter to issue queries on our data stores.

Querysets
**********

Just like in Django, querysets provide a high-level API to query, exclude, filter results from our stores.
Internally, querysets build query objects, that are then interpreted by the refined store.

Backends
********

We try to keep lifter's code as agnostic and generic as possible.

Because of that, logic that is specific to a data source should be stored in a dedicated module, such modules being named ``backends``.

Lifter comes build-in with a :doc:`few backends </backends/index>`, the most advanced being the Python backend. However, work is in progress
to implement file and HTTP backends.

The query language
-------------------

At the moment, lifter support two ways two make queries:

1. the explicit engine, which looks like SQLAlchemy. Example: `manager.filter(User.age == 42)`. **This is the recommended engine for any new project**
2. the keyword engine, which looks like Django. Example: `manager.filter(age=42)`. This is the engine that was built-in in the first release of the package.

Internally, lifter converts all queries to the explicit engine. This mean if you do `manager.filter(age=42)`,
lifter will convert it to `manager.filter(User.age == 42)`.

.. warning::

    We recommend using the explicit engine for any new projects involving lifter. The keyword engine will be kept
    for backward compatibility until and if a deprecation plan is adopted.
