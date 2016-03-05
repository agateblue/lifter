==========================
Performance considerations
==========================

Under the hood, lifter uses plain Python code and, therefore, is just a higher level
API to interact with iterables.

It means lifter queries will always be slower than vanilla Python filtering/querying
using comprehension lists and for loops. If performance is critical in your application,
and lifter is not fast enough, you'll have to use another tool.

At the moment, lifter is much, much more slower than vanilla Python equivalent (from 10x to 100x, depending
on your dataset and the kind of filtering you apply). You can get an up to date comparison
by running the benchmark suite:

.. code-block:: shell

    # Get the code and install the package
    git clone git@github.com:EliotBerriot/lifter.git
    cd lifter
    python setup.py install

    # run the whole benchmark suite
    python -m tests.benchmarks

    # Run a subset of benchmarks
    python -m tests.benchmarks single_filter combined_filter

Lifter performance is a huge concern and as it's API become more stable, focus
will progressively move on from implementing new features to optimizing current ones.

If you want to help with that, by reporting a performance pitfall, fixing one, or even writing a benchmark,
your contribution is welcome!
