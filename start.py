import sys
from aio.weibo_cn_async import WeiboCnSpider

if __name__ == '__main__':
    args = sys.argv[1:]

    WeiboCnSpider(tasks=4).start(args)
