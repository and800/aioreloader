import sys
import os
from asyncio import AbstractEventLoop, sleep
from types import ModuleType


_started = False
_files = set()


def start(loop: AbstractEventLoop, interval=0.5):
    global _started
    if _started:
        return
    _started = True

    modify_times = {}
    _call_periodically(loop, interval, _check_all, modify_times)


def watch(path):
    _files.add(path)


def _call_periodically(loop: AbstractEventLoop, interval, callback, *args):
    async def wrap():
        while True:
            await sleep(interval)
            callback(*args)
    return loop.create_task(wrap())


def _check_all(modify_times):
    for module in sys.modules.values():
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
        os.execv(sys.executable, [sys.executable] + sys.argv)
