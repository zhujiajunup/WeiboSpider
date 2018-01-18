import asyncio
import time

now = lambda: time.time()

async def work(x):
    print('waiting: ', x)
    await asyncio.sleep(x)
    return 'Done after {}s'.format(x)


def callback(future):
    print('ret: ', future.result())

start = now()
tasks = []
for i in range(3):
    task = asyncio.ensure_future(work(1 << i))
    task.add_done_callback(callback)
    tasks.append(task)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))

print('time:', now() - start)