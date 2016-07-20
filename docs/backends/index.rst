Backends
========

Lifter is bundled with a few backends, the main one being the :doc:`Python backend <python>`, that operates on Python iterables.

However, you are not limited to querying Python iterables. Lifter is designed to be backend-agnostic. Therefore, it's simple
enough to make lifter talk to other data sources, such as a SQL database, a REST API, a LDAP store, a file...

We we use the term backend, we mainly designate a dedicated :py:class:`Store` implementation, because the store is responsible
for compiling a generic query, sending it to the underlying data source and return results. A backend, though, could also include dedicated
models, parsers or adapters.


Contents:

.. toctree::
   :maxdepth: 1

   python
