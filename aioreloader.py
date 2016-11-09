import sys
import os
import subprocess
import asyncio
from types import ModuleType

_abstract_loop = asyncio.AbstractEventLoop

_started = False
_reload_attempted = False
_files = set()


def start(loop: _abstract_loop, interval=0.5):
    global _started
    if _started:
        return
    _started = True

    modify_times = {}
    _call_periodically(loop, interval, _check_all, modify_times)


def watch(path):
    _files.add(path)


def _call_periodically(loop: _abstract_loop, interval, callback, *args):
    @asyncio.coroutine
    def wrap():
        while True:
            yield from asyncio.sleep(interval)
            callback(*args)
    return loop.create_task(wrap())


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
        sys.exit(0)
    else:
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except OSError:
            os.spawnv(
                os.P_NOWAIT,
                sys.executable,
                [sys.executable] + sys.argv
            )
            os._exit(0)
