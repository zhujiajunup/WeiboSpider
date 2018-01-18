import pymysql
from aio.weibo_redis import RedisJob
from weibo_cn import JobType
import asyncio
import aiomysql


async def aio_repair(loop, sql):
    pool = await aiomysql.create_pool(host='localhost', port=3306, user='root', password='1111', db='graduate2', loop=loop)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
                await cursor.execute(sql)
                for row in await cursor.fetchall():
                    print(row)

async def repair_user():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='1111', database='graduate2')
    cursor = conn.cursor()
    cursor.execute('select id from weibo_user')
    redis_job = RedisJob()

    for row in cursor.fetchall():
        await redis_job.push_job(JobType.user.value, {'user_id': row[0]})
        print(row[0])
    cursor.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(aio_repair(loop, 'select id from weibo_user limit 1'))
loop.close()

