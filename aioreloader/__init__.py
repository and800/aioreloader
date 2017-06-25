"""
Port of tornado reloader to asyncio.
Reloads your asyncio-based application automatically
when you modify the source code.

https://github.com/and800/aioreloader
"""

from ._contents import start, watch

__version__ = '0.0.1'