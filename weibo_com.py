from time import sleep
from setting import LOGGER
from redis_cookies import RedisCookies
import random
import user_agents
import requests
from bs4 import BeautifulSoup
import re
import json
import traceback
from queue import Queue
import threading


class WeiboComSpider:
    def __init__(self):
        self.comment_queue = Queue()
        self.info_map = {
            '昵称': 'nickname',
            '真实姓名': 'realname',
            '所在地': 'location',
            '性别': 'gender',
            '性取向': 'sexual_ori',
            '感情状况': 'emotion_state',
            '生日': 'birthday',
            '血型': 'blood_type',
            '博客': 'blog',
            '个性域名': 'domain_name',
            '简介': 'intro',
            '注册时间': 'register_time',
            '邮箱': 'email',
            '公司': 'company',
            '大学': 'college',
            '高中': 'high_school',
            '初中': 'mid_school',
            '标签': 'tags',
        }

    def crawl_comment(self):
        while True:
            # try:
                comment_url = self.comment_queue.get()
                self.comment2(comment_url)
            # except Exception:
            #     LOGGER.error(traceback.format_exc())
            #     sleep(10)

    def start(self):
        self.info('1316949123')

    @staticmethod
    def get_header():
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'weibo.com',
            # 'Referer': 'https://weibo.com',
            'User-Agent': user_agents.USER_AGENTS[random.randint(0, len(user_agents.USER_AGENTS) - 1)]
        }
        return header

    @staticmethod
    def find_fm_view_json(html):
        resp_html = BeautifulSoup(html, 'html.parser')
        scripts = resp_html.find_all('script')
        scripts.reverse()
        fm_view_pattern = re.compile('FM.view\((.*)\)')
        view_jsons = []
        for script in scripts:
            r = fm_view_pattern.findall(script.string)
            if len(r):
                view_jsons.append(json.loads(r[0]))
        return view_jsons

    def comment2(self, tweet_url):
        pass

    def comment(self, tweet_url):
        comment_api = 'https://weibo.com/aj/v6/comment/big?' \
                      'ajwvr=6&id=4183679670408501&root_comment_max_id=292480698116801' \
                      '&root_comment_max_id_type=0&root_comment_ext_param=&' \
                      'page=2'
        comment_url = tweet_url.split('?')[0] + '?type=comment'
        LOGGER.info('comment task: %s' % comment_url)
        cookies_json = RedisCookies.fetch_cookies()
        cookies = cookies_json['cookies']
        headers = self.get_header()
        headers['Upgrade-Insecure-Requests'] = '1'
        headers['Proxy-Connection'] = 'keep-alive'
        # headers['Referer'] = comment_url
        try_time = 0
        comment_html_str = ''
        while try_time < 2:
            resp_text = requests.get(url=comment_api, headers=headers, cookies=cookies, verify=False).text
            print(resp_text)
            views_json = self.find_fm_view_json(html=resp_text)

            for view_json in views_json:
                if 'plc_main' == view_json['domid']:
                    comment_html_str = view_json['html']

                    break
            if comment_html_str != '':
                comment_html = BeautifulSoup(comment_html_str, 'html.parser')
                comments = comment_html.find_all(attrs={'node-type': 'root_comment'})
                break
            else:
                try_time += 1

    def info(self, user_id):
        base_home_url = 'https://weibo.com/p/100306%s/info?mod=pedit_more' % user_id
        LOGGER.info('info task: %s' % base_home_url)
        cookies_json = RedisCookies.fetch_cookies()
        cookies = cookies_json['cookies']
        headers = self.get_header()
        session = requests.Session()
        session2 = requests.Session()
        headers['Host'] = 'weibo.com'
        headers['Referer'] = 'https://weibo.com/p/100306%s/home' % user_id
        # https://weibo.com/p/1003061316949123/home?from=page_100306&mod=TAB&is_all=1
        # 'http://weibo.com/2606356035/fans?from=100505&wvr=6&mod=headfans&current=fans'
        headers['Upgrade-Insecure-Requests'] = '1'
        headers.pop('Connection')
        headers.pop('Accept')
        headers['Proxy-Connection'] = 'keep-alive'
        try_time = 0
        info_html = ''
        info_html_str = ''
        while try_time < 10:
            resp_text = session.get(url=base_home_url, headers=headers, cookies=cookies, verify=False).text
            resp_text2 = requests.get(url=base_home_url, headers=headers, verify=False).text
            print(resp_text2)
            view_json = self.find_fm_view_json(html=resp_text)
            for r_json in view_json:
                if 'Pl_Official_PersonalInfo__58' == r_json['domid']:
                    info_html_str = r_json['html']
                    break
            if info_html_str != '':
                info_html = BeautifulSoup(info_html_str, 'html.parser')
                iframe = info_html.find_all('iframe')
                if not iframe:
                    break
            try_time += 1

        if info_html != '':
            # user = User()
            # user.user_id = user_id
            # if not db_session.query(exists().where(User.user_id == user_id)).scalar():
            #     db_session.add(user)
            #     db_session.commit()
            lis = info_html.find_all('li', 'clearfix')
            info_dict = {}
            for li in lis:
                try:
                    title = li.find('span', 'pt_title').text
                    pt_detail = li.find('span', 'pt_detail')
                    all_a = pt_detail.find_all('a')
                    if all_a:
                        detail = ','.join([a.text for a in all_a])
                    else:
                        detail = pt_detail.text

                    detail = detail.replace('\n', '').replace('\t', '').replace('\r', '')

                    value = self.info_map.get(title[:-1], None)
                    if value:
                        info_dict[value] = detail
                except:
                    LOGGER.error('info task error: %s' % traceback.format_exc())
                    continue
            # app.send_task('tasks.user.fans', args=(user_id,))
            if info_dict:
                LOGGER.info('info task result: %s' % info_dict)
                # try:
                #     db_session.query(User).filter(User.user_id == user_id).update(info_dict)
                #     db_session.commit()
                # except:
                #     db_session.rollback()
                #     LOGGER.error('info task error: %s' % traceback.format_exc())
            return info_dict
        return None


if __name__ == '__main__':
    WeiboComSpider().comment('https://weibo.com/6014513352/Fz6Td1IgJ')
    # WeiboComSpider().start()
