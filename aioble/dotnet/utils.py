import asyncio
from collections import Awaitable

from System import Action
from System.Threading.Tasks import Task

async def wrap_dotnet_task(task, loop):
    done = asyncio.Event()
    task.ContinueWith(Action[Task](lambda x: loop.call_soon_threadsafe(done.set)))
    await done.wait()
    if task.IsFaulted:
        raise Exception(task.Exception.ToString())
    return task.Result