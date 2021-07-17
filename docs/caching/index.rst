==========================
Caching
==========================

.. module:: lifter.caches

.. currentmodule:: lifter.caches

Lifter offers a built-in caching mechanism that can be used store query results and retrieve them later.

This is an efficient way to reduce the I/O of your application, avoid reaching rate limites, suffer from network latency, etc.

Caching is configured on store creation, via the following API:

.. code-block:: python

    from lifter import caches
    from lifter import models
    from lifter.backend import http

    class MyModel(models.Model):
        class Meta:
            app_name = 'my_app'
            name = 'my_model'

    cache = caches.DummyCache()
    store = http.RESTStore(identifier='my_store', cache=cache)
    manager = store.query(MyModel)

You can use the same :py:class:`Cache` instance across multiple store if you want, this won't lead to cache collisions.


How does it work?
******************

When a cache is configured for a given store and the store execute a query, the following happens:

1. The store identifier, the model app, the model name and the query are hashed together to form a cache key
2. The cache is then queried using that key
3. If a result is found with that key, it's returned directly without sending the query to the underlying backend
4. If no result is found, the query is processed normally, but result will be stored in the cache for further use

Once a cache is configured for a store, it is automatically used:

.. code-block:: python

    # This will execute the query and store results in the cache
    manager.all().count()

    # For this one, the query won't execute, since the value is present in the cache
    manager.all().count()

For the previous example, the cache key will look like::

    my_store:my_app:my_model:ee26b0dd4af7e749aa1a

Cache options
********************

The following arguments are available to all cache instances, all are optional.

``default_timeout``
-------------------

.. attribute:: Cache.default_timeout

The default timeout in seconds that will be used for cached values.
Defaults to ``None``, meaning the value will never expire.


``enabled``
-------------------

.. attribute:: Cache.enabled

Wether the cache is enabled by default or not.

.. note::

    You can override this behaviour by using :py:meth:`Cache.disable` and
    :py:meth:`Cache.enable` context managers


Cache methods
**************

.. autoclass:: Cache
    :members: get, set, get_or_set, disable, enable

Available cache backends
************************

At the moment, the only cache backend available is the :py:class:`DummyCache`, that store values in a Python dictionary.

You can use it's code as a starting point to implement your own backends, using Redis or Memcached, for example.
