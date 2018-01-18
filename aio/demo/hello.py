import asyncio
import threading


@asyncio.coroutine
def hello(msg):
    cnt = 0
    while True:
        cnt += 1
        print('say: %s %d tims (%s)' % (msg, cnt, threading.current_thread().getName()))
        yield from asyncio.sleep(1)


@asyncio.coroutine
def hello1(msg):
    cnt = 0
    while True:
        cnt += 1
        print('say: %s %d tims (%s)' % (msg, cnt, threading.current_thread().getName()))
        yield from asyncio.sleep(2)

async def hello2(msg):
    cnt = 0
    while True:
        cnt += 1
        print('say: %s %d tims (%s)' % (msg, cnt, threading.current_thread().getName()))
        await asyncio.sleep(0.1)

print(type(hello("123")))
print(asyncio.iscoroutine(hello))
loop = asyncio.get_event_loop()
tasks = [hello('hello world'), hello1('hello python'), hello2('hello aio')]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
