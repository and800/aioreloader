import sys
import os
import subprocess
import asyncio
from types import ModuleType

try:
    ensure_future = asyncio.ensure_future
except AttributeError:
    ensure_future = getattr(asyncio, 'async')

abstract_loop = asyncio.AbstractEventLoop

task = None
reload_attempted = False
files = set()


def start(loop: abstract_loop = None, interval: float = 0.5) -> asyncio.Task:
    """
    Start the reloader: create the task which is watching
    loaded modules and manually added files via ``watch()``
    and reloading the process in case of modification, and
    attach this task to the loop.
    """
    if loop is None:
        loop = asyncio.get_event_loop()

    global task
    if not task:
        modify_times = {}
        task = call_periodically(loop, interval, check_all, modify_times)
    return task


def watch(path: str) -> None:
    """
    Add any file to the watching list.
    """
    files.add(path)


def call_periodically(loop: abstract_loop, interval, callback, *args):
    @asyncio.coroutine
    def wrap():
        while True:
            yield from asyncio.sleep(interval, loop=loop)
            callback(*args)
    return ensure_future(wrap(), loop=loop)


def check_all(modify_times):
    if reload_attempted:
        return
    for module in list(sys.modules.values()):
        if not isinstance(module, ModuleType):
            continue
        path = getattr(module, '__file__', None)
        if not path:
            continue
        check(path, modify_times)
    for path in files:
        check(path, modify_times)


def check(target, modify_times):
    time = os.stat(target).st_mtime
    if target not in modify_times:
        modify_times[target] = time
        return
    if modify_times[target] != time:
        reload()


def reload():
    global reload_attempted
    reload_attempted = True
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
