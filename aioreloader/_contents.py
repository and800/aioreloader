import sys
import os
import os.path
import subprocess
import asyncio
import hashlib
from concurrent.futures import ThreadPoolExecutor
from types import ModuleType
from typing import Callable


hook_type = Callable[[], None]
abstract_loop = asyncio.AbstractEventLoop

task = None
reload_attempted = False
reload_hook = None
files = set()
checksum_files = set()


def start(
    loop: abstract_loop = None, interval: float = 0.5, hook: hook_type = None
) -> asyncio.Task:
    """
    Start the reloader.

    Create the task which is watching loaded modules
    and manually added files via ``watch()``
    and reloading the process in case of modification.
    Attach this task to the loop.

    If ``hook`` is provided, it will be called right before
    the application goes to the reload stage.
    """
    if loop is None:
        loop = asyncio.get_event_loop()

    global reload_hook
    if hook is not None:
        reload_hook = hook

    global task
    if not task:
        modify_times = {}
        checksums = {}
        executor = ThreadPoolExecutor(1)
        task = call_periodically(
            loop,
            interval,
            check_and_reload,
            modify_times,
            checksums,
            executor,
        )
    return task


def watch(path: str, checksum: bool = False) -> None:
    """Add any file to the watching list."""
    if checksum:
        checksum_files.add(path)
    else:
        files.add(path)


def call_periodically(loop, interval, callback, *args):
    async def wrap():
        while True:
            await asyncio.sleep(interval)
            await callback(*args, loop=loop)

    return asyncio.ensure_future(wrap(), loop=loop)


async def check_and_reload(modify_times, checksums, executor, loop: abstract_loop):
    if reload_attempted:
        return
    files_changed = await loop.run_in_executor(
        executor, check_all, modify_times, checksums
    )
    if files_changed:
        reload()


def check_all(modify_times, checksums):
    for module in list(sys.modules.values()):
        if not isinstance(module, ModuleType):
            continue
        path = getattr(module, "__file__", None)
        if not path or not os.path.isfile(path):
            continue
        if check(path, modify_times):
            return True
    for path in files:
        if check(path, modify_times):
            return True
    for path in checksum_files:
        if check(path, modify_times) and checksum_check(path, checksums):
            return True
    return False


def check(target, modify_times):
    time = os.stat(target).st_mtime
    if target not in modify_times:
        modify_times[target] = time
        return False
    return modify_times[target] != time


def get_checksum(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        data = f.read()
        h.update(data)

    return h.hexdigest()


def checksum_check(target, checksums):
    checksum = get_checksum(target)
    if target not in checksums:
        checksums[target] = checksum
        return False
    return checksums[target] != checksum


def reload():
    global reload_attempted
    reload_attempted = True

    if reload_hook is not None:
        reload_hook()

    xopt = []
    if hasattr(sys, "_xoptions") and sys._xoptions:
        for k, v in sys._xoptions.items():
            if type(v) == bool:
                xopt.append("-X{}".format(k))
            else:
                xopt.append("-X{}={}".format(k, v))

    if sys.platform == "win32":
        subprocess.Popen([sys.executable] + xopt + sys.argv)
        sys.exit(os.EX_OK)
    else:
        try:
            os.execv(sys.executable, [sys.executable] + xopt + sys.argv)
        except OSError:
            os.spawnv(
                os.P_NOWAIT,
                sys.executable,
                [sys.executable] + xopt + sys.argv,
            )
            os._exit(os.EX_OK)
