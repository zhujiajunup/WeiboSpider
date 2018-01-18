# WeiboSpider
- python asyncio、aioredis、aiohttp，全程协程速度不要太快
- 任务、cookies保存在redis中，实现分布式，想什么时候爬就什么时候爬，想开几个线程、几台机器爬随意
- 稍微计算下，每个账号使用别使用太频繁，比如登录了100个账号，差不多开10个协程就好了，平摊到每个账号差不多10s使用一次
- 代码很烂，逻辑很乱，欢迎吐槽，欢迎交流。
## 微博登录获取cookie
1. 使用selenium自动化登录，先在weibo.com登录，在跳转到weibo.cn（实现电脑端->手机端cookies的转换，cn页面解析起来更方便）
2. 验证码使用了[云打码](http://www.yundama.com),具体使用看官网介绍
3. cookies保存在redis
4. 微博账号购买传送门,买那个一块钱12个就可以了（[http://www.onini.cn/bxfehnqv](http://www.onini.cn/bxfehnqv)）
## 微博抓取
任务保存在redis中，解析的是weibo.cn页面，爬虫处理逻辑在```aio.weibo_cn_async.py```。

解析后的数据发送到kafka中

所以，你的机器应该有如下环境
- win7+
- redis
- kafka
- python 3.4+
- aioredis
- aiohttp
- selenum
- 火狐浏览器最新版（怎么使用自行百度）

## 开始抓取任务
### 初始化配置
在项目更目录创建conf文件夹，放入```weibo.yaml```，内容为：
```yaml
accounts:
  - user: '用户1'
    password: '密码1'
  - user: '用户2'
    password: '密码2'

yundama:
  user: '云打码用户'
  password: '云打码密码'
```
 ### 保存cookies
 直接运行根目录下的```redis_cookies.py```文件
 ```commandline
python redis_cookies.py
```
运行完毕后， redis下应该有两个key，```users```和```account```, ```users```是set结构，```account```是hset结构

数据长什么样自己去看吧。

### 初始化任务
自己看```init_job.py```代码，有示例
```commandline
python init_job.py
```
### 运行爬虫

在根目录中运行
```
python start.py [u| w| f| c]
```
- u代表只抓微博用户信息
- w表示抓用户发布的微博
- f表示抓取用户的关注用户
- c表示抓取微博的所有评论

可自由组合，可以多开几个

emmmm.....有疑问发送邮件zhujiajunup@163.com


