from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from redis_cookies import RedisCookies
import os
from time import sleep
from PIL import Image
from code_recognize import YunDaMa
from setting import PROPERTIES
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# dcap = dict(DesiredCapabilities.PHANTOMJS)
# driver = webdriver.PhantomJS(desired_capabilities=dcap)
browser = webdriver.Firefox()
browser.maximize_window()
yun_da_ma = YunDaMa(username=PROPERTIES['yundama']['user'], password=PROPERTIES['yundama']['password'])


def save_verify_code_img():
    screen_shot_path = '.\\img\\screenshot.png'
    code_img_path = '.\\img\\verify_code.png'
    browser.save_screenshot(screen_shot_path)
    code_img = browser.find_element_by_xpath('//img[@node-type="verifycode_image"]')
    left = code_img.location['x']
    top = code_img.location['y']
    right = code_img.location['x'] + code_img.size['width']
    bottom = code_img.location['y'] + code_img.size['height']
    print(left, top, right, bottom)
    picture = Image.open(screen_shot_path)
    picture = picture.crop((1422, 300, 1533, 334))
    picture.save(code_img_path)
    # os.remove(screen_shot_path)
    return code_img_path


def login(weibo_user, weibo_password):
    try_time = 10
    browser.get('https://weibo.com/login.php')
    username = browser.find_element_by_id("loginname")
    username.clear()
    username.send_keys(weibo_user)
    psd = browser.find_element_by_xpath('//input[@type="password"]')
    psd.clear()
    psd.send_keys(weibo_password)
    commit_btn = browser.find_element_by_xpath('//a[@node-type="submitBtn"]')
    commit_btn.click()
    # 没那么快登录成功
    sleep(8)
    while try_time:
        try:
            # 如果登录不成功是有验证码框的
            browser.find_element_by_xpath('//div[@node-type="verifycode_box"]')
            code_input = browser.find_element_by_xpath('//input[@node-type="verifycode"]')
            code_input.send_keys('  ')
            img_path = save_verify_code_img()

            while not os.path.exists(img_path):
                print(img_path + "not exist")
                sleep(1)
            print(img_path)
            captcha_id, code_text = yun_da_ma.recognize(img_path)
            # os.remove(img_path)
            code_str = bytes.decode(code_text)
            print('recognize result: %s' % code_str)

            code_input.clear()
            code_input.send_keys(code_str)
            commit_btn = browser.find_element_by_xpath('//a[@node-type="submitBtn"]')
            commit_btn.click()
            # 稍等一会
            sleep(5)
            try_time -= 1
            break
        except NoSuchElementException:
            print('login success')
            break
    browser.get('https://weibo.cn/1316949123/info')
    sleep(2)
    cookies_dict = {}
    for elem in browser.get_cookies():
        cookies_dict[elem['name']] = elem['value']
        print(elem["name"], elem["value"])
    RedisCookies.save_cookies(weibo_user, cookies_dict)


# def home():
# browser.get('https://weibo.com/47452014')
# browser.get('https://weibo.cn/1316949123/info')

# RedisCookies.clean()
# login()
# home()

# cookies_json = RedisCookies.fetch_cookies()
# # driver.delete_all_cookies()
# cookies = cookies_json['cookies']
# for k, v in cookies.items():
#     print(k, v)
#     driver.add_cookie({'name': k, 'value': v})
# driver.get('https://weibo.com/6014513352/Fz6Td1IgJ')
# print(driver.page_source)
