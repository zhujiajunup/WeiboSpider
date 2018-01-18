import asyncio
import datetime

start = datetime.datetime.now()
async def first():
    print('hello world')

loop = asyncio.get_event_loop()
coroutine = first()
task = loop.create_task(coroutine)
print(task)
loop.run_until_complete(task)
print(task)
loop.close()
print('cost: %d' % (datetime.datetime.now() - start).microseconds)
