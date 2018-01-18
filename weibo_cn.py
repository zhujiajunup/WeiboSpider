# -*- coding:utf-8 -*-
import json
import random
import re
import datetime
import traceback
from queue import Queue
from time import sleep
import threading
import requests
import sys
from enum import Enum
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import urllib3
import user_agents
from redis_cookies import RedisCookies, RedisJob
from setting import LOGGER, THREAD_NUM
from pybloom import ScalableBloomFilter
from memory_collect import getsize

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WeiboProcuder:
    def __init__(self, bootstrap_servers, topic):
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                      value_serializer=lambda msg: json.dumps(msg).encode('utf-8'))

    def send(self, msg, url):
            LOGGER.info(url)
            LOGGER.info('send type: %s, id: %s, (%s)' % (msg['type'], msg['id'], str(msg)))
            self.producer.send(topic=self.topic, value=msg)
            LOGGER.info('send successful.')


class JobType(Enum):
    comment = 'comment'
    tweet = 'tweet'
    follower = 'follower'
    user = 'user'
    repost = 'repost'


class WeiboCnSpider:
    def __init__(self):
        self.bloom_filter = ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        self.weibo_limit = False
        self.time_current_pattern = re.compile(r'(\d*)分钟前')
        self.time_today_pattern = re.compile(r'今天\s*(\d*):(\d*)')
        self.time_year_pattern = re.compile(r'(\d*)月(\d*)日\s*(\d*):(\d*)')
        self.user_id_pattern = re.compile(r'https://weibo.cn/u/(\d*)')
        self.weibo_host = 'https://weibo.cn'
        self.follow_url = self.weibo_host + '/%s/follow'

        self.fan_url = self.weibo_host + '/%s/fans'
        self.user_info_url = self.weibo_host + '/%s/info'
        self.user_tweet_url = self.weibo_host + '/%s'
        self.user_tweet_url2 = self.weibo_host + '/%s?page=%d'
        self.user_repost_url = self.weibo_host + '/repost/%s'
        self.user_repost_url2 = self.weibo_host + '/repost/%s?page=%d'
        self.tweet_comment_url = self.weibo_host + '/comment/%s'
        self.tweet_comment_url2 = self.weibo_host + '/comment/%s?page=%d'
        self.weibo_producer = WeiboProcuder(['localhost:9092'], 'sinaweibo')

    def crawl_user(self):
        while True:
            user_job_info = RedisJob.fetch_job(JobType.user.value)
            if user_job_info:
                try:
                    self.grab_user_info(user_job_info['user_id'])
                    # self.weibo_queue.put({'url': self.user_tweet_url % user_id, 'uid': user_id})
                    # self.follow_queue.put({'uid': user_id, 'url': self.follow_url % user_id})
                except:
                    LOGGER.error(traceback.format_exc())
                    sleep(5 * 60)
            else:
                sleep(1)

    def crawl_follow(self):
        while True:
            follow_dict = RedisJob.fetch_job(JobType.follower.value)
            if follow_dict:
                try:
                    self.grab_follow(follow_dict)

                except:
                    LOGGER.error(traceback.format_exc())
                    sleep(5 * 60)

    def crawl_comment(self):
        while True:
            comment_job_info = RedisJob.fetch_job(JobType.comment.value)
            if comment_job_info:
                try:
                    self.grab_tweet_comments(comment_job_info)
                    
                except:
                    LOGGER.error("something error")
                    LOGGER.error(traceback.format_exc())
                    sleep(5 * 60)

    def crawl_weibo(self):
        while True:
            tweet_job_info = RedisJob.fetch_job(JobType.tweet.value)
            if tweet_job_info:
                try:
                    self.grab_user_tweet(tweet_job_info)
                except:
                    LOGGER.error(traceback.format_exc())
                    sleep(5 * 60)

    def crawl_repost(self):
        while True:
            repost_job_info = RedisJob.fetch_job(JobType.repost.value)
            if repost_job_info:
                try:
                    self.grab_tweet_repost(repost_job_info)
                except:
                    LOGGER.error(traceback.format_exc())
                    sleep(5 * 60)

    def grab_view(self, user_id):
        """
        获取用户id的微博数、粉丝数、发布的微博数
        :param user_id: 用户id
        :return: dict
        """
        LOGGER.info('grab user view: %s' % str(user_id))
        session = requests.Session()
        cookies = RedisCookies.fetch_cookies()
        response = session.get(self.weibo_host+'/' + str(user_id), cookies=cookies['cookies'], verify=False)
        home_page_html = BeautifulSoup(response.text, "lxml")
        v = home_page_html.find('div', class_='tip2')
        result = {}
        if v:
            content = v.get_text(';')
        else:
            content = ''
        tweet_r = re.findall('微博\[(\d+)\];', content)
        result['tweetNum'] = tweet_r[0] if tweet_r else -1
        fans_r = re.findall('粉丝\[(\d+)\];', content)
        result['fansNum'] = fans_r[0] if fans_r else -1
        follow_r = re.findall('关注\[(\d+)\];', content)
        result['followNum'] = follow_r[0] if follow_r else -1
        return result

    def grab_tweet_repost(self, repost_url):
        LOGGER.info('grab tweet repost: %s' % str(repost_url))
        session = requests.Session()
        cookies = RedisCookies.fetch_cookies()
        response = session.get(repost_url['url'], cookies=cookies['cookies'], verify=False)
        repost_html = BeautifulSoup(response.text, "lxml")
        reposts = repost_html.find_all('div', class_='c')
        for repost in reposts:
            tweet_info = {}

            attr_span = repost.find('span', class_='cc')
            if attr_span:
                attitude_url = attr_span.extract().find('a').get('href')
                tweet_id = attitude_url.split('/')[2]
                tweet_info['id'] = tweet_id
                RedisJob.push_job(JobType.comment.value,
                                  {'url': 'https://weibo.cn/comment/%s' % tweet_id, 'tweetId': tweet_id})
                # self.comment_queue.put({'url': 'https://weibo.cn/comment/%s' % tweet_id, 'tweetId': tweet_id})
            else:
                continue

            time_tool_text = repost.find('span', class_='ct').extract().get_text()
            time_tool = time_tool_text.split('\u6765\u81ea')
            tweet_info['time'] = self.get_time(time_tool[0])
            if len(time_tool) == 2:
                source = time_tool[1]
                tweet_info['source'] = source
            tweet_info['flag'] = '转发'
            user_href = repost.find('a').get('href')
            if user_href.startswith('/u/'):
                user_id = user_href[3:]
            else:
                user_id = self.get_user_id_from_homepage(self.weibo_host + user_href)
            tweet_info['uid'] = user_id
            self.user_id_in_queue(user_id)
            tweet_content = repost.get_text()
            tweet_info['content'] = tweet_content
            tweet_info['sourceTid'] = repost_url['tweetId']
            tweet_info['type'] = 'tweet_info'
            self.weibo_producer.send(tweet_info, repost_url['url'])
        if 'page=' not in repost_url['url']:
            page_div = repost_html.find(id='pagelist')
            if page_div:
                max_page = int(page_div.input.get('value'))

                for page in range(2, max_page + 1):
                    RedisJob.push_job(JobType.repost.value,
                                      {'url': self.user_repost_url2 % (repost_url['tweetId'], page),
                                       'tweetId': repost_url['tweetId']})

    def get_time(self, time_str):
        current_result = self.time_current_pattern.findall(time_str)
        time_now = datetime.datetime.now()
        if current_result:
            result_time = time_now - datetime.timedelta(minutes=int(current_result[0]))
            return result_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            current_result = self.time_today_pattern.findall(time_str)
            if current_result:
                result_time = datetime.datetime(time_now.year, time_now.month,
                                                time_now.day, int(current_result[0][0]), int(current_result[0][0]))
                return result_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                current_result = self.time_year_pattern.findall(time_str)
                if current_result:
                    result_time = datetime.datetime(time_now.year, int(current_result[0][0]),
                                                    int(current_result[0][1]), int(current_result[0][2]),
                                                    int(current_result[0][3]))
                    return result_time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    return time_str

    def start(self, args):
        # self.user_queue.put('6037294528')
        # self.grab_user_info('1316949123')
        # return self.grab_user_info('1316949123')

        # self.get_follow({'uid': '2365758410', 'url': self.follow_url % '2365758410'})
        # RedisJob.push_job(JobType.comment.value, {'url': 'https://weibo.cn/comment/FCa7KxpHE', 'tweetId': 'FCa7KxpHE'})

        for i in range(0, THREAD_NUM):
            if 'f' in args:
                follow_thread = threading.Thread(target=self.crawl_follow, name='follow_thread_'+str(i))
                follow_thread.start()
            if 'c' in args:
                comment_thread = threading.Thread(target=self.crawl_comment, name='comment_thread_'+str(i))
                comment_thread.start()
            if 'u' in args:
                user_thread = threading.Thread(target=self.crawl_user, name='user_thread_'+str(i))
                user_thread.start()
            # self.weibo_queue.put({'url': self.user_tweet_url % '277118746', 'uid': '277118746'})
            if 'w' in args:
                weibo_thread = threading.Thread(target=self.crawl_weibo, name='weibo_thread_'+str(i))
                weibo_thread.start()
            # self.repost_queue.put({'url': self.user_repost_url % 'FCoPpaIQp', 'tweetId': 'FCoPpaIQp'})
            if 'r' in args:
                repost_thread = threading.Thread(target=self.crawl_repost, name='repost_thread_'+str(i))
                repost_thread.start()


    def grab_follow(self, follow_dict):
        LOGGER.info('start grab user follow: %s' % str(follow_dict))
        session = requests.Session()
        cookies = RedisCookies.fetch_cookies()
        response = session.get(self.follow_url % follow_dict['uid'], cookies=cookies['cookies'], verify=False)
        follow_html = BeautifulSoup(response.text, "lxml")
        all_td = follow_html.find_all('td', style=True)
        for td in all_td:
            a = td.find('a').get('href')
            usr_id_result = self.user_id_pattern.findall(a)
            if usr_id_result:
                usr_id = usr_id_result[0]
            else:
                usr_id = self.get_user_id_from_homepage(a)
            public_user = td.parent.find_all('img', src='https://h5.sinaimg.cn/upload/2016/05/26/319/5338.gif')
            if not public_user:
                enterprise_user = td.parent.find_all('img', src='https://h5.sinaimg.cn/upload/2016/05/26/319/5337.gif')
                if not enterprise_user:
                    self.user_id_in_queue(usr_id)
                else:
                    LOGGER.info('%s passed' % usr_id)
            else:
                LOGGER.info('%s passed' % usr_id)
        if 'page=' not in follow_dict['url']:

            page_div = follow_html.find(id='pagelist')
            if page_div:
                max_page = int(page_div.input.get('value'))
                for page in range(2, max_page + 1):
                    RedisJob.push_job(JobType.follower.value,
                                      {'url': (self.follow_url % follow_dict['uid']) + '?page=' + str(page),
                                       'uid': follow_dict['uid']})

    def get_fans(self, user_id):
        pass

    def user_id_in_queue(self, user_id):
        if user_id and user_id not in self.bloom_filter:
            # LOGGER.info('%s in user queue.' % user_id)
            self.bloom_filter.add(user_id)
            RedisJob.push_job(JobType.user.value, {'user_id': user_id})

    @staticmethod
    def get_header():
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
            'Host': 'weibo.cn',
            'Referer': 'https://weibo.cn',
            'User-Agent': user_agents.USER_AGENTS[random.randint(0, len(user_agents.USER_AGENTS) - 1)]
        }
        return header

    @staticmethod
    def get_user_id_from_homepage(home_page):
        session = requests.Session()
        cookies = RedisCookies.fetch_cookies()
        response = session.get(home_page, cookies=cookies['cookies'], verify=False)
        home_page_html = BeautifulSoup(response.text, "lxml")
        info_a = home_page_html.find('a', string='资料')
        # LOGGER.info('get id from home page: %s' % home_page)
        if info_a:
            user_id = info_a.get('href').split('/')[1]
            # LOGGER.info('id got: %s' % user_id)
            return user_id
        return 0

    def grab_tweet_comments(self, comment_url):
        LOGGER.info('start grab comment: %s' % str(comment_url))
        session = requests.Session()
        cookies = RedisCookies.fetch_cookies()
        response = session.get(comment_url['url'], cookies=cookies['cookies'], verify=False)
        response.encoding = 'utf-8'
        comment_html = BeautifulSoup(response.text, "lxml")

        comment_divs = comment_html.find_all(id=re.compile('C_[\d]'), class_='c')
        for comment_div in comment_divs:
            comment_info = {}
            comment_id = comment_div.get('id')
            user_a = comment_div.find('a')
            if user_a:
                user_href = user_a.get('href')
                if user_href.startswith('/u/'):
                    user_id = user_href[3:]
                else:
                    user_id = self.get_user_id_from_homepage(self.weibo_host + user_href)
                self.user_id_in_queue(user_id)
                comment_info['userId'] = user_id
                comment_info['content'] = comment_div.find(class_='ctt').get_text()
                others = comment_div.find(class_='ct').get_text()
                if others:
                    others = others.split('\u6765\u81ea')
                    comment_info['pubTime'] = self.get_time(others[0])
                    if len(others) == 2:
                        comment_info['source'] = others[1]
                comment_info['id'] = comment_id
                comment_info['tweetId'] = comment_url['tweetId']
                comment_info['type'] = 'comment_info'
                self.weibo_producer.send(comment_info, comment_url['url'])

        if 'page=' not in comment_url['url']:
            RedisJob.push_job(JobType.repost.value, {'url': self.user_repost_url % comment_url['tweetId'],
                                                     'tweetId': comment_url['tweetId']})
            tweet_div = comment_html.find(id='M_', class_='c')
            if tweet_div:
                tweet_user_a = tweet_div.find('a')
                flag = False
                if tweet_user_a:
                    tweet = {}
                    tweet_user_href = tweet_user_a.get('href')
                    if tweet_user_href.startswith('/u/'):
                        tweet_user_id = tweet_user_href[3:]
                    else:
                        tweet_user_id = self.get_user_id_from_homepage(self.weibo_host + tweet_user_href)
                    if tweet_div.find(class_='cmt', string='转发理由:'):
                        flag = True
                    else:
                        tweet_content = tweet_div.find('span', class_='ctt').get_text()
                        tweet['content'] = tweet_content
                    tweet_details = list(
                        filter(lambda div: div.find(class_='pms'),
                               comment_html.find_all('div', id=False, class_=False)))
                    detail = tweet_details[0].get_text(';').replace('\xa0', '')
                    like = re.findall(u'\u8d5e\[(\d+)\];', detail)  # 点赞数
                    transfer = re.findall(u'\u8f6c\u53d1\[(\d+)\];', detail)  # 转载数
                    comment = re.findall(u'\u8bc4\u8bba\[(\d+)\];', detail)  # 评论数
                    tweet['id'] = comment_url['tweetId']
                    tweet['like'] = like[0] if like else 0
                    tweet['transfer'] = transfer[0] if transfer else 0
                    tweet['comment'] = comment[0] if comment else 0
                    tweet['type'] = 'tweet_info'
                    if flag:
                        self.weibo_producer.send(tweet, comment_url['url'])
                    else:
                        others = tweet_div.find(class_='ct').get_text()
                        if others:
                            others = others.split('\u6765\u81ea')
                            tweet['time'] = self.get_time(others[0])
                            if len(others) == 2:
                                tweet['source'] = others[1]
                        tweet['uid'] = tweet_user_id
                        self.weibo_producer.send(tweet, comment_url['url'])

            page_div = comment_html.find(id='pagelist')
            if page_div:

                max_page = int(page_div.input.get('value'))
                for page in range(2, max_page + 1):
                    RedisJob.push_job(JobType.comment.value,
                                      {'url': self.tweet_comment_url2 % (comment_url['tweetId'], page),
                                       'tweetId': comment_url['tweetId']})

    def grab_user_tweet(self, tweet_url):
        LOGGER.info('start grab tweet: %s' % str(tweet_url))
        session = requests.Session()
        cookies = RedisCookies.fetch_cookies()
        response = session.get(tweet_url['url'], cookies=cookies['cookies'], verify=False)
        response.encoding = 'utf-8'
        user_tweet_html = BeautifulSoup(response.text, "lxml")

        tweet_divs = user_tweet_html.find_all(id=True, class_='c')
        for tweet_div in tweet_divs:
            tweet = {}
            if tweet_div.find(class_='cmt', string='转发理由:'):  # 转发
                tweet['flag'] = '转发'
                parent = tweet_div.find(class_='cmt', string='转发理由:').parent
                try:
                    comment_href = tweet_div.find_all('div')[-2].find('a', class_='cc').get('href')

                    href = comment_href.split('?')[0]
                    tweet['sourceTid'] = href.split('/')[-1]

                except Exception:
                    pass
                text = parent.get_text()
                fields = text.split('\xa0')

                content = fields[0][5:]
                ct_content = parent.find('span', class_='ct').get_text()
                time_source = ct_content.split('\u6765\u81ea')

                time = time_source[0]
                if len(time_source) == 2:
                    source = time_source[1]
                else:
                    source = 'unknown'
                other = ';'.join(fields[1:])

            else:
                tweet['flag'] = '原创'
                text = tweet_div.get_text()
                ct_content = tweet_div.find('span', class_='ct').get_text()
                time_source = ct_content.split('\u6765\u81ea')

                time = time_source[0]
                if len(time_source) == 2:
                    source = time_source[1]
                else:
                    source = 'unknown'
                fields = text.split('\u200b')
                content = fields[0]
                other_fields = fields[-1].split('\xa0')
                other = ';'.join(other_fields[1:])

            like = re.findall(u'\u8d5e\[(\d+)\];', other)  # 点赞数
            transfer = re.findall(u'\u8f6c\u53d1\[(\d+)\];', other)  # 转载数
            comment = re.findall(u'\u8bc4\u8bba\[(\d+)\];', other)  # 评论数
            tweet['content'] = content
            tweet['id'] = tweet_div.get('id')
            tweet['time'] = time
            tweet['source'] = source
            tweet['like'] = like[0] if like else -1
            tweet['transfer'] = transfer[0] if transfer else -1
            tweet['comment'] = comment[0] if comment else -1
            tweet['type'] = 'tweet_info'
            tweet['uid'] = tweet_url['uid']

            self.weibo_producer.send(tweet, tweet_url['url'])
            # 获取评论
            # self.comment_queue.put({'url': self.tweet_comment_url % tweet['id'][2:],
            #                         'tweetId': tweet['id'][2:]})

        if 'page=' not in tweet_url['url']:

            # total_weibo_span = user_tweet_html.find('span', class_='tc')
            # if total_weibo_span:
            #     total_result = re.findall('微博\[(\d*)\]', total_weibo_span.get_text())
            #     if total_result:
            #         total = total_result[0]
            #         if int(total) > 5000:
            #             return
            #     else:
            #         return
            # else:
            #     return
            page_div = user_tweet_html.find(id='pagelist')
            if page_div:
                max_page = int(page_div.input.get('value'))
                if self.weibo_limit:
                    max_page = max_page if max_page < 10 else 10
                for page in range(2, max_page + 1):
                    RedisJob.push_job(JobType.tweet.value, {'url': self.user_tweet_url2 % (tweet_url['uid'], page),
                                                            'uid': tweet_url['uid']})

    def grab_user_info(self, user_id):
        LOGGER.info('start grab user info: %s' % user_id)
        session = requests.Session()
        cookies = RedisCookies.fetch_cookies()
        cookie = ''
        for k, v in cookies['cookies'].items():
            cookie = cookie + k + '=' + v + ';'
        response = session.get(self.user_info_url % user_id, cookies=cookies['cookies'], verify=False)

        response.encoding = 'utf-8'
        user_info_html = BeautifulSoup(response.text, "lxml")
        div_list = list(user_info_html.find_all(class_=['c', 'tip']))

        base_info_index, edu_info_index, work_info_index = -1, -1, -1
        base_info = ''
        edu_info = ''
        work_info = ''
        tags = ''
        user_info = {}
        for index, div in enumerate(div_list):
            text = div.text
            if text == u'基本信息':
                base_info_index = index
            elif text == u'学习经历':
                edu_info_index = index
            elif text == u'工作经历':
                work_info_index = index
        if base_info_index != -1:
            b = div_list[base_info_index + 1]
            tags = ','.join(map(lambda a: a.get_text(), b.find_all('a')))
            base_info = b.get_text(';')
        if edu_info_index != -1:
            edu_info = div_list[edu_info_index + 1].get_text(';')

        if work_info_index != -1:
            work_info = div_list[work_info_index + 1].get_text(';')

        nickname = re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', base_info)  # 昵称
        if nickname:
            user_info['nickname'] = nickname[0] if nickname else 'unknown'
            gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', base_info)  # 性别
            place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', base_info)  # 地区（包括省份和城市）
            signature = re.findall(u'\u7b80\u4ecb[:|\uff1a](.*?);', base_info)  # 个性签名
            birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?);', base_info)  # 生日
            sex_orientation = re.findall(u'\u6027\u53d6\u5411[:|\uff1a](.*?);', base_info)  # 性取向
            marriage = re.findall(u'\u611f\u60c5\u72b6\u51b5[:|\uff1a](.*?);', base_info)  # 婚姻状况
            head_url = user_info_html.find('img', alt='头像')
            if head_url:
                user_info['head'] = head_url.get('src')
            user_info['tags'] = tags
            user_info['gender'] = gender[0] if gender else 'unknown'
            user_info['place'] = place[0] if place else 'unknown'
            user_info['signature'] = signature[0] if signature else 'unknown'
            user_info['birthday'] = birthday[0] if birthday else 'unknown'
            user_info['sexOrientation'] = sex_orientation[0] if sex_orientation else 'unknown'
            user_info['eduInfo'] = edu_info if edu_info else 'unknown'
            user_info['marriage'] = marriage[0] if marriage else 'unknown'
            user_info['workInfo'] = work_info if work_info else 'unknown'

            user_info['type'] = 'user_info'
            user_info['id'] = user_id
            result = self.grab_view(user_id)
            user_info.update(result)
            self.weibo_producer.send(user_info, self.user_info_url % user_id)


if __name__ == '__main__':
    args = sys.argv[1:]
    LOGGER.info(args)
    WeiboCnSpider().start(args)
