"""
Port of tornado reloader to asyncio.
Reloads your asyncio-based application automatically
when you modify the source code.

https://github.com/and800/aioreloader
"""

import sys
import os
import subprocess
import asyncio
from types import ModuleType

__version__ = '0.0.1'

try:
    ensure_future = asyncio.ensure_future
except AttributeError:
    ensure_future = getattr(asyncio, 'async')

_abstract_loop = asyncio.AbstractEventLoop

_task = None
_reload_attempted = False
_files = set()


def start(loop: _abstract_loop = None, interval: float = 0.5) -> asyncio.Task:
    """
    Start the reloader: create the task which is watching
    loaded modules and manually added files via ``watch()``
    and reloading the process in case of modification, and
    attach this task to the loop.
    """
    if loop is None:
        loop = asyncio.get_event_loop()

    global _task
    if not _task:
        modify_times = {}
        _task = _call_periodically(loop, interval, _check_all, modify_times)
    return _task


def watch(path: str) -> None:
    """
    Add any file to the watching list.
    """
    _files.add(path)


def _call_periodically(loop: _abstract_loop, interval, callback, *args):
    @asyncio.coroutine
    def wrap():
        while True:
            yield from asyncio.sleep(interval, loop=loop)
            callback(*args)
    return ensure_future(wrap(), loop=loop)


def _check_all(modify_times):
    if _reload_attempted:
        return
    for module in list(sys.modules.values()):
        if not isinstance(module, ModuleType):
            continue
        path = getattr(module, '__file__', None)
        if not path:
            continue
        _check(path, modify_times)
    for path in _files:
        _check(path, modify_times)


def _check(target, modify_times):
    time = os.stat(target).st_mtime
    if target not in modify_times:
        modify_times[target] = time
        return
    if modify_times[target] != time:
        _reload()


def _reload():
    global _reload_attempted
    _reload_attempted = True
    if sys.platform == 'win32':
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(os.EX_OK)
    else:
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except OSError:
            os.spawnv(
                os.P_NOWAIT,
                sys.executable,
                [sys.executable] + sys.argv,
            )
            os._exit(os.EX_OK)
