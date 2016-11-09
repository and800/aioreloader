aioreloader
===========

Tool that reloads your asyncio-based application automatically when you
modify the source code.

Usage
-----

Here's an example of usage with
`aiohttp <https://github.com/KeepSafe/aiohttp>`_ framework:

.. code-block:: python
    
    app = aiohttp.web.Application()
    aioreloader.start(app.loop)
    aiohttp.web.run_app(app)
    
Requirements
------------

Python - at least 3.4
