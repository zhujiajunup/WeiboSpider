from aio.weibo_redis import RedisJob
from weibo_cn import JobType
import asyncio


loop = asyncio.get_event_loop()
# loop.run_until_complete(RedisJob().push_job(JobType.comment.value,
#                                             {'url': 'https://weibo.cn/comment/FEr40v4uH', 'tweetId': 'FEr40v4uH'}))
# loop.run_until_complete(RedisJob().push_job(JobType.tweet.value, {'url': 'https://weibo.cn/1316949123', 'uid': '1316949123'}))
# loop.run_until_complete(RedisJob().push_job(JobType.follower.value, {'url': 'https://weibo.cn/1316949123/follow', 'uid': '1316949123'}))
loop.run_until_complete(RedisJob().push_job(JobType.user.value, {'user_id': '1316949123'}))

loop.close()

