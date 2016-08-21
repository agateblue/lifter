=======
History
=======

RefinedStore removal

RefinedStore where entirely removed from lifter, resulting in a cleaner API / logic.
You can now implement your own backend simply by creating you own `Store` class.


0.4.1 (2016-8-2)
------------------

This release fix issue #42: some files were not included in lifter distribution,
mainly the ``backends`` and ``contrib`` directories, causing various imports to fail.


0.4 (2016-7-20)
---------------

This release introduces the django contrib module to enable filtering with lifter's python backend
on a django queryset, effectively reducing number of queries sent to the database.

Work is also in progress regarding caching (see #39) but this is not over yet.

0.3 (2016-7-12)
---------------

This is a big release, that breaks backward-compatibility with previous ones.

This release implements a new flow to help implementing #33. The general idea
is to make lifter generic and be able to query any data source with it.

The 0.3 release sets the foundation for that by moving all python-iterable related code to a dedicated backend,
and by implementing the Store -> Adapter > Model layout to deal with queries and result parsing.

An additional, very simple, ``filesystem`` backend is provided to demonstrate how you can implement your own datasource in lifter.

The work, though, is still incomplete, because the `filesystem` store internally uses the `IterableStore` from the python backend.

A real store (such as REST or SQL) would be able to understand queries and pass them to a real backend (PostgreSQL).

Anyway, we're in the good direction here :)

0.2.1 (2016-3-4)
----------------

This is a small release, with a few improvements on ordering API and on the overall documentation:

* Can now order using multiple fields, fix #30
* [Backward incompatible] Can now invert ordering in explicit engine using path and ~ operator. Passing a `reverse` argument to `order_by` is not possible anymore
* Can now query for field existences, fix #26


0.2 (2016-2-23)
---------------

This is quite an important release:

* A whole new API is now available to make queries, see #15 for more information [angru, eliotberriot]
* Querysets are now lazy
* A brand new documentation is now available at http://lifter.readthedocs.org
* Splitted some huge files into submodules for more clarity

Considering the new query API, we basically switched from django's ORM-style (keyword engine)
to SQLAlchemy style (explicit engine).

The keyword engine is still available and will continue to work as before.
It is neither under depreciation at the moment, but using the new engine is recommended.

0.1.1 (2016-2-21)
------------------

* Can now pass arguments to underlying manager via lifter.load
* Random order_by for queryset [Pentusha]
* Improve code examples readability in readme
* Removed duplicate method on queryset [Mec-iS]
* Can now run some lookups within iterables (WIP) [Ogreman].
* Lots of improvements and corrections (typos, examples, etc.) in README [johnfraney, youtux]
* Can now return flat lists as results for aggregates [Ogreman]


0.1.0 (2016-2-17)
------------------

* First release on PyPI.
