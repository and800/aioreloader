aioreloader
===========

Tool that reloads your asyncio-based application automatically when you
modify the source code.

Most of code has been borrowed from
`Tornado <https://github.com/tornadoweb/tornado/blob/master/tornado/autoreload.py>`_
reloader built mostly by `@finiteloop <https://github.com/finiteloop>`_
and `@bdarnell <https://github.com/bdarnell>`_. Thanks!

Usage
-----

Here's an example of usage with
`aiohttp <https://github.com/KeepSafe/aiohttp>`_ framework:

.. code-block:: python

    app = aiohttp.web.Application()
    aioreloader.start()
    aiohttp.web.run_app(app)

Requirements
------------

Python - at least 3.3

Installation
------------
.. code-block:: bash

    $ pip install aioreloader
