import os
import time
import random
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from requests import Session

load_dotenv(find_dotenv())

username = os.environ.get('username')
password = os.environ.get('password')

code_url = 'http://www.5iads.cn/module/user/code.asp'
login_url = 'http://www.5iads.cn/module/user/login.asp'
sgin_url = 'http://www.5iads.cn/module/user/Signin.asp'
ad_url = 'http://www.5iads.cn/module/dianji/'
surf_url = 'http://www.5iads.cn/module/surf/'

session = Session()
session.headers = {
	'Accept': 'application/json, text/javascript, */*; q=0.01',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Connection': 'keep-alive',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Host': 'www.5iads.cn',
	'Origin': 'http://www.5iads.cn',
	'Referer': 'http://www.5iads.cn/',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
	'X-Requested-With': 'XMLHttpRequest'
}

# 更新验证码
for _ in range(7):
	response = session.get(code_url)
	if response.text == 'http://www.5iads.cn/yzmfile/7.jpg|/t.asp?id=7|success':
		break

# 登录
user_data = {
	'action': 'loginsys',
	'Username': username,
	'Password': password,
	'checkcode': '50'
}
response = session.post(login_url, data=user_data)

# 签到
response = session.get(sgin_url, params=dict(action='signin'))

# 获取广告列表
data = {
	'action': 'loadDianjiList',
	'row': '20',
	'pagenum': '1'
}
response = session.post(ad_url, data=data)
ad_list = [ad['id'] for ad in response.json()]
print(ad_list)

# 点击广告
def click_ad(ad_id):
	data ={
		'Isjiami': 'false',
		'clickid': ad_id,
		'action': 'Show_dianji_getone',
	}
	response = session.post(ad_url, data=data)
	return response.json()

# 等待广告计时
def wait_ad(ad_info):
	time.sleep(7 + ad_info.get('miao', 20))

# 完成广告
def finish_ad(ad_info):
	data = {
		'action': ad_info['action'],
		'firstCk': 2,
		'YzmCheck': 'success',
		'clickid': ad_info['id'],
		'refurl': 'http://www.5iads.cn/reclick.asp?gourl=http://www.5iads.cn/zhuan.asp?zhuan=dianji',
		'sign': ad_info['sign'],
		'Isjiami': True,
		'key': random.random()
	}
	response = session.post(ad_url, data=data)
	print(response.text)

for ad in ad_list:
	ad_info = click_ad(ad)
	wait_ad(ad_info)
	finish_ad(ad_info)

# 广告冲浪开始
def start_surf():
	data = {
		'des': 'start',
		'type': 1,
		'manual': 0,
		'info': 'window_1',
		'timeB': None,
		'timeE': None,
	}
	time_now = int(datetime.now().timestamp())
	data['timeB'] = time_now
	data['timeE'] = time_now
	response = session.post(surf_url, data=data)
	print(response.text)
	surf_info = response.json()
	return surf_info
# 等待广告
def wait_surf():
	time.sleep(20)
# 广告冲浪结束
def finish_surf(surf_info):
	data = {
		'des': 'complete',
		'type': 1,
		'manual': 0,
		'info': 'window_1',
		'sign': None,
		'timeB': None,
		'timeE': None,
		'id': None,
	}
	time_now = int(datetime.now().timestamp())
	data['timeB'] = time_now
	data['timeE'] = time_now
	data['sign'] = surf_info['sign']
	data['id'] = surf_info['id']
	response = session.post(surf_url, data=data)
	print(response.text)

for _ in range(10):
	surf_info = start_surf()
	wait_surf()
	finish_surf(surf_info)


session.close()