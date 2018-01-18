import asyncio
import time

now = lambda: time.time()

async def work(x):
    print('waiting: ', x)
    await asyncio.sleep(x)
    return 'done after {}s'.format(x)

async def main():
    tasks = [asyncio.ensure_future(work(1 << i)) for i in range(3)]
    return await asyncio.gather(*tasks)
    # dones, pendings = await asyncio.wait(tasks)
    # for task in dones:
    #     print('task ret: ', task.result())


start = now()

loop = asyncio.get_event_loop()
results = loop.run_until_complete(main())
for result in results:
    print('ret: ', result)
print('time: ', now() - start)