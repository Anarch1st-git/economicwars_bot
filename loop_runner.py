import asyncio
from threading import Thread

loop = asyncio.new_event_loop()


def run_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()


def start_loop_in_background():
    thread = Thread(target=run_loop, daemon=True)
    thread.start()


def run_async_task(coro):
    return asyncio.run_coroutine_threadsafe(coro, loop)
