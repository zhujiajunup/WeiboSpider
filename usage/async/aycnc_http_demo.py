import aiohttp
import asyncio
import async_timeout
from redis_cookies import RedisCookies


# http://aiohttp.readthedocs.io/en/stable/index.html
async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            html = await response.text()
            print(html)


async def main():
    cookies = RedisCookies.fetch_cookies()
    async with aiohttp.ClientSession(cookies=cookies['cookies']) as session:
        fetch(session, 'https://weibo.cn/1316949123/info')


loop = asyncio.get_event_loop()
loop.run_until_complete(main())