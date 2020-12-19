# -*- coding: utf-8 -*-
# @Time    : 2020/12/19 20:56
# @Author  : MENGYU R
# @File    : fzu_new.py
# @Software: PyCharm
import time
import pymysql
import requests
from urllib.parse import urljoin
from lxml import etree
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36 Edg/80.0.361.54',
    'Host': 'news.fzu.edu.cn',
}


# check that if the link can respond correctly and return response.text or response.status_code
def get_page(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return response.status_code


# parse into news page and grab date_time, author, headline, read_count, main_text
def parse_to_news_page(html):
    # date_time
    date_time_pattern = re.compile("id..fbsj.>(.*?)</span>", re.S)
    date_time = re.findall(date_time_pattern, html)[0]
    print("日期: ", date_time, end='')

    # author
    author_pattern = re.compile("<span.*?author.*?>(.*?)</span>", re.S)
    author = re.findall(author_pattern, html)[0]
    print(" 作者: ", author, end='')

    # headline
    headline_pattern = re.compile("<title>(.*?)-福州大学新闻网</title>", re.S)
    headline = re.findall(headline_pattern, html)[0]
    print(" 标题: ", headline, end='')

    # read_count
    page_id_pattern = re.compile("getDocReadCount.do....(.*?)..timeout", re.S)
    page_id = re.findall(page_id_pattern, html)
    read_count_page = requests.get(url='http://news.fzu.edu.cn//interFace/getDocReadCount.do?id=' + page_id[0],
                                   headers=headers)
    read_count_pattern = re.compile(".*", re.S)
    read_count = re.findall(read_count_pattern, read_count_page.text)[0]
    print(" 阅读量: ", read_count)

    # main_text
    html = etree.HTML(html)
    main_text = html.xpath('//*[@id="news_content_display"]/p//text()')
    main_text = "".join(main_text)
    print("正文:\n", main_text)

    # store in database
    sql = 'insert into fzu_new_grab(date_time, author, headline,read_count,main) values(%s, %s, %s, %s, %s)'
    cursor.execute(sql, (date_time, author, headline, read_count, main_text))
    db.commit()


# parse into main page
def parse_to_main_page(html):
    html = etree.HTML(html)
    href = html.xpath('//*[@id="main"]/div[2]/div[2]/ul/li/a/@href')  # get links to every news item

    # traverse every url
    for item in href:
        main_url = urljoin('http://news.fzu.edu.cn/html/fdyw/1.html', item)  # merge links
        main_html = get_page(main_url)  # to check that if the link can respond correctly
        parse_to_news_page(main_html)  # to grab date_time, author, headline, read_count and main_text


# change pages
def main(offset):
    main_url = 'http://news.fzu.edu.cn/html/fdyw/' + str(offset) + '.html'  # get every main page url
    html = get_page(main_url)  # get every page html
    parse_to_main_page(html)


if __name__ == '__main__':

    # store in database
    db = pymysql.connect(host='localhost', user='root', password='1234', port=3306, db='fzu_new')
    cursor = db.cursor()
    cursor.execute("drop table if EXISTS fzu_new_grab")  # if exists fzu_new_catch table, use execute drop table

    # create database table
    sql_createTb = """CREATE TABLE fzu_new_grab (
                     id INT NOT NULL AUTO_INCREMENT,
                     date_time CHAR(80),
                     author CHAR(80),
                     headline CHAR(80),
                     read_count int,
                     main TEXT,
                     PRIMARY KEY(id))
                     """
    cursor.execute(sql_createTb)

    # grab five pages of content
    for i in range(5):
        main((i + 1))
        time.sleep(5)
