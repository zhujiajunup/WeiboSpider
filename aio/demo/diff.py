from threading import Thread
import time
import asyncio


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def do_work(x):
    print('waiting {}'.format(x))
    await asyncio.sleep(x)
    return 'done after {}s'.format(x)


def more_work(x):
    print('more work {}'.format(x))
    time.sleep(x)
    print('finished. {}'.format(x))


start = time.time()
new_loop = asyncio.new_event_loop()
t = Thread(target=start_loop, args=(new_loop, ))
t.start()
# new_loop.call_soon_threadsafe(more_work, 5)
# new_loop.call_soon_threadsafe(more_work, 6)
f1 = asyncio.run_coroutine_threadsafe(do_work(5), new_loop)
f2 = asyncio.run_coroutine_threadsafe(do_work(4), new_loop)
print('time: {}'.format(time.time() - start))
print(f1.result())
print(f2.result())
