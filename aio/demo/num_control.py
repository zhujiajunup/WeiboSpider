from threading import BoundedSemaphore, Thread
import asyncio


class Uest:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.sem = BoundedSemaphore(10)

    @staticmethod
    def start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def work(self):
        count = 1
        while True:
            asyncio.run_coroutine_threadsafe(self.do_work(), self.loop)
            count += 1

    @staticmethod
    async def do_work():
        print('do work ')
        await asyncio.sleep(1)
        print('finish')
        return None

    def start(self):
        t = Thread(target=self.start_loop, args=(self.loop,))
        t.setDaemon(True)
        t.start()
        asyncio.run_coroutine_threadsafe(self.work(), self.loop)


if __name__ == '__main__':
    Uest().start()
