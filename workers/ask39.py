import aiohttp
import asyncio
import async_timeout
import re
import csv
from bs4 import BeautifulSoup

host = 'http://ask.39.net'
answer_cnt_pattern = re.compile('精选回答\((\d*)\)')
async def fetch(session, url):
    async with async_timeout.timeout(60):
        async with session.get(url) as response:
            return await response.text()

async def parse_question(session, url):
    print(url)
    html = await fetch(session, url)
    html = BeautifulSoup(html, 'lxml')
    title = html.find('title').get_text()
    if title.endswith('页面不存在'):
        return None
    ask_cont = html.find('div', class_='ask_cont')
    ask_hid = ask_cont.find('div', class_='ask_hid').find('p').get_text(";")
    txt_label = ask_cont.find('p', class_='txt_label')
    labels = txt_label.find_all('span', style=False)
    lbs = []
    for label in labels:
        lbs.append(label.get_text())
    selected = html.find('div', class_='selected')
    sele_img = selected.find('p', 'sele_img')
    if sele_img:
        sele_img = sele_img.get_text()
    else:
        sele_img = selected.find('p', 'answe1').get_text()
    
    answers = answer_cnt_pattern.findall(sele_img)
    first_doctor = selected.find('div', class_='doc_img').find('a').get('href')
    # print('-' * 100)
    # print(url)
    # print(ask_hid.strip())
    # print(';'.join(lbs))
    # print(answers[0])
    # print(first_doctor)
    return (url.strip(), ask_hid.strip(), ';'.join(lbs), answers[0], first_doctor.strip())

async def test():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'http://ask.39.net/question/52945721.html')
        html = BeautifulSoup(html, 'lxml')
        
        print()


async def main():
    details = []
    async with aiohttp.ClientSession() as session:
        for i in range(1, 200):
            html = await fetch(session, 'http://ask.39.net/news/237-%d.html' % i)
            html = BeautifulSoup(html, 'lxml')

            list_tags = html.find('div', id='list_tag', class_='list_tag')
            print(list_tags is None)
            ask_lis = list_tags.find('ul').find_all('li')

            for li in ask_lis:
                detail = await parse_question(session, host + li.find('a').get('href'))
                print(detail)
                if detail:
                    details.append(detail)
                # print(html)
    with open('questions.csv', 'a', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerows(details)
            


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())