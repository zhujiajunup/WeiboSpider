# WeiboSpider
python 3.4+
aioredis
aiohttp
asyncio
selenum
beautifulsoup4

## 微博登录获取cookie
1. 使用selenium，先在weibo.com登录，在跳转到weibo.cn
2. 验证码使用了[yundama](www.yundama.com),具体使用看官网介绍
3. cookies保存在redis
4. 微博账号购买传送门（）
## 微博抓取
任务保存在redis中，解析的是weibo.cn页面，爬虫处理逻辑在```weibo_cn_async.py```

## 开始抓取任务
在项目更目录创建conf文件夹，放入

