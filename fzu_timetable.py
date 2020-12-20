# -*- coding: utf-8 -*-
# @Time    : 2020/12/20 10:20
# @Author  : MENGYU R
# @File    : fzu_timetable.py
# @Software: PyCharm
import requests
import re
import prettytable as pt

stu_id = input("账号")
stu_pass = input("密码")

data = {
    'muser': stu_id, 'passwd': stu_pass
}

url = 'http://59.77.226.32/logincheck.asp'  # login url

# Create table
tb = pt.PrettyTable()
tb.field_names = ["星期一", "星期二", "星期三", "星期四", "星期五"]  # table header

# Using session to maintain session
session = requests.Session()
session.headers.update({
    'Referer': 'http://jwch.fzu.edu.cn/login.aspx',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101Firefox/83.0',
})

res = session.post(url=url, data=data, timeout=10)  # Post information and goto personal page

# Because the courses in the timetable are not in the personal page,
# but hidden in another page, so we have to go to another page
pattern_right = re.compile("top.........(.*?)..noresize", re.S)
page_id = re.findall(pattern_right, res.text)[0]
page_url = 'http://59.77.226.35/right.aspx?id=' + page_id

per_page = session.get(url=page_url, timeout=10)  # Get information and goto course page

# course regular expression
course_pattern = re.compile("font.color..#9A1B1B.>(.*?)</font>", re.S)
course = re.findall(course_pattern, per_page.text)

# create course table
tb.padding_width = 3
tb.add_row(course[0:5])
tb.add_row(course[5:10])
tb.add_row(course[10:15])
tb.add_row(course[15:20])
tb.add_row(course[20:25])
tb.add_row(course[25:30])
tb.add_row(course[30:35])
tb.add_row(course[35:40])
tb.padding_width = 4
tb.align = 'c'
print(tb)
