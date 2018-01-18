from aio.weibo_redis import RedisJob
from weibo_cn import JobType
import asyncio


loop = asyncio.get_event_loop()
# loop.run_until_complete(RedisJob().push_job(JobType.comment.value,
#                                             {'url': 'https://weibo.cn/comment/FEr40v4uH', 'tweetId': 'FEr40v4uH'}))
# loop.run_until_complete(RedisJob().push_job(JobType.tweet.value, {'url': 'https://weibo.cn/2210643391', 'uid': '2210643391'}))
# loop.run_until_complete(RedisJob().push_job(JobType.follower.value, {'url': 'https://weibo.cn/2210643391/follow', 'uid': '2210643391'}))
loop.run_until_complete(RedisJob().push_job(JobType.user.value, {'user_id': '2210643391'}))

loop.close()
# RedisJob.push_job(JobType.comment.value, {'url': 'https://weibo.cn/comment/FDThJFjTG', 'tweetId': 'FDThJFjTG'})
# RedisJob.push_job(JobType.user.value, {'user_id': '2210643391'})

