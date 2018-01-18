import time
import asyncio

now = lambda : time.time()

async def worker(x):
    print('waiting:', x)
    return 'Done after {}s'.format(x)


def callback(future):
    print('callback: ', future.result())

start = now()

coroutine = worker(2)
loop = asyncio.get_event_loop()
task = asyncio.ensure_future(coroutine)
task.add_done_callback(callback)
loop.run_until_complete(task)

print('time: ', now() - start)

