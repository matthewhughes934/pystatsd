======================
A Python statsd client
======================

statsd_ is a friendly front-end to Graphite_. This is a Python client
for the statsd daemon.

.. image:: https://dl.circleci.com/status-badge/img/gh/matthewhughes934/pystatsd/tree/master.svg?style=svg
   :target: https://dl.circleci.com/status-badge/redirect/gh/matthewhughes934/pystatsd/tree/master
   :alt: CircleCI build status

.. image:: https://img.shields.io/pypi/v/statsd.svg
   :target: https://pypi.python.org/pypi/statsd/
   :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/statsd.svg
   :target: https://pypi.python.org/pypi/statsd/
   :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/wheel/statsd.svg
   :target: https://pypi.python.org/pypi/statsd/
   :alt: Wheel Status

:Code:          https://github.com/matthewhughes934/pystatsd
:License:       MIT; see LICENSE file
:Issues:        https://github.com/jsocol/pystatsd/issues
:Documentation: https://matthewhughes934.github.io/pystatsd/

Quickly, to use:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125)
    >>> c.incr('foo')  # Increment the 'foo' counter.
    >>> c.timing('stats.timed', 320)  # Record a 320ms 'stats.timed'.

You can also add a prefix to all your stats:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125, prefix='foo')
    >>> c.incr('bar')  # Will be 'foo.bar' in statsd/graphite.


Installing
==========

The easiest way to install statsd is with pip!

You can install from PyPI::

    $ pip install statsd

Or GitHub::

    $ pip install -e https://github.com/matthewhughes934/pystatsd#egg=statsd

Or from source::

    $ git clone https://github.com/matthewhughes934/pystatsd
    $ cd pystatsd
    $ python setup.py install


Docs
====

There are lots of docs in the ``docs/`` directory and on ReadTheDocs_.


.. _statsd: https://github.com/etsy/statsd
.. _Graphite: https://graphite.readthedocs.io/
.. _ReadTheDocs: https://statsd.readthedocs.io/en/latest/index.html
