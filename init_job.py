import asyncio
from aio.weibo_redis import RedisJob
from aio.weibo_cn_async import WeiboCnSpider, JobType
loop = asyncio.get_event_loop()
# loop.run_until_complete(RedisJob().push_job(JobType.comment.value,
#                                             {'url': 'https://weibo.cn/comment/G7lbPgeeC', 'tweetId': 'G7lbPgeeC'}))
async def task():
    spider = WeiboCnSpider()
    job = await RedisJob().fetch_job(JobType.search.value)
    print(job)
    await spider.search_tweet(job)
loop.run_until_complete(task())
# loop.run_until_complete(RedisJob().clean())
# loop.run_until_complete(RedisJob().push_job(JobType.repost.value,
#                                             {'url': 'https://weibo.cn/repost/G7lbPgeeC', 'tweetId': 'G7lbPgeeC'}))
# loop.run_until_complete(RedisJob().push_job(JobType.tweet.value, {'url': 'https://weibo.cn/1316949123', 'uid': '1316949123'}))
# loop.run_until_complete(RedisJob().push_job(JobType.follower.value, {'url': 'https://weibo.cn/1316949123/follow', 'uid': '1316949123'}))
# loop.run_until_complete(RedisJob().push_job(JobType.user.value, {'user_id': '1316949123'}))

loop.close()
