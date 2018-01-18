import asyncio

async def run():
    await run2()
    await run3()
    pass

async def hello():
    print('hello')
    asyncio.sleep(1)

async def run2():
    print('run2 sleep')
    hello()
    print('run2 weakup')
    pass

async def run3():
    print('run3 sleep')
    hello()
    print('run3 weakup')
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
loop.close()