=======
History
=======

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
