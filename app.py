import os
import time
import hashlib
import functools
from datetime import datetime
from dotenv import load_dotenv
from requests_html import HTMLSession

class Adrobot:
	login_url = 'http://wx.m.5iads.cn/module/login.asp'
	signin_url = 'http://wx.m.5iads.cn/module/signin.asp'
	browser_url = 'http://wx.m.5iads.cn/module/browser.asp'
	withdraw_url = 'http://wx.m.5iads.cn/module/tixian.asp'

	referer_urls = dict(
		login_referer = 'http://wx.m.5iads.cn/login.html',
		signin_referer = 'http://wx.m.5iads.cn/Signin.html?t=',
		browser_referer = 'http://wx.m.5iads.cn/browser_wx.html?t=',
		withdraw_referer = 'http://wx.m.5iads.cn/tixian.html?t='
	)

	debug = False

	def __init__(self):
		dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
		load_dotenv(verbose=True, dotenv_path=dotenv_path)
		self.username = os.getenv("adrobot_username")
		self.password = os.getenv("adrobot_password")
		self.phonenum = os.getenv("adrobot_phonenum")
		self.withdraw_amount = os.getenv("withdraw_amount")
		self.withdraw_weekday = os.getenv("withdraw_weekday")

		self.data = dict()

		self.session = HTMLSession()
		self.session.headers = {
			'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Connection': 'keep-alive',
			'Content-Type': 'application/x-www-form-urlencoded',
			'Host': 'wx.m.5iads.cn',
			'Origin': 'http://wx.m.5iads.cn',
			'Referer': 'http://wx.m.5iads.cn/',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
			'X-Requested-With': 'XMLHttpRequest'
		}

	def __del__(self):
		self.session.close()

	@property
	def password(self):
		return self._password

	@password.setter
	def password(self, value):
		md5 = hashlib.md5()
		md5.update(value.encode(encoding='utf-8'))
		self._password = md5.hexdigest()

	def change_referer(with_timestamp=True):
		def decorator(func):
			@functools.wraps(func)
			def wrapper(self, *args, **kw):
				if with_timestamp:
					timestamp = int(datetime.now().timestamp())
				else:
					timestamp = ''
				referer_url = self.referer_urls[func.__name__.split('_')[0] + '_referer'] + str(timestamp)
				self.session.headers['Referer'] = referer_url
				self.data.clear()
				self.data.update(gotourl=referer_url,)
				return func(self, *args, **kw)
			return wrapper
		return decorator

	@change_referer(with_timestamp=False)
	def login(self):
		self.data.update(
			action='loginsys',
			username=self.username,
			password=self.password,
		)
		response = self.session.post(self.login_url, data=self.data)
		if self.debug: print(response.text)
		return response

	@change_referer()
	def signin(self):
		self.data.update(action='signin')
		response = self.session.post(self.signin_url, data=self.data)
		if self.debug: print(response.text)
		return response
	
	@change_referer()
	def browser_get_ads(self):
		self.data.update(
			action='loadDianjiList',
			page = 1,
			beginTime = '',
			endTime = '',
			)
		response = self.session.post(self.browser_url, data=self.data)
		ads = filter(None, response.json().get('rows'))
		return ads

	@change_referer()
	def browser_click_ad(self, ad):
		self.data.update(
			action='Show_dianji_getone',
			clickid = ad['id'],
			)
		response = self.session.post(self.browser_url, data=self.data)
		finish_info = response.json()
		try:
			response = self.session.get(ad.get('url', 'www.baidu.com'))
		except:
			pass
		time.sleep(ad.get('miao', 20) + 3)
		return finish_info

	@change_referer()
	def browser_finish_ad(self, finish_info):
		self.data.update(
			action='BrowserJiangli',
			clickid = finish_info['id'],
			sign = finish_info['sign'],
			endTime = '',
			)
		response = self.session.post(self.browser_url, data=self.data)
		if self.debug: print(response.text)
		return response

	def browser(self):
		ads = self.browser_get_ads()
		for ad in ads:
			finish_info = self.browser_click_ad(ad)
			self.browser_finish_ad(finish_info)
		return ads

	@change_referer()
	def withdraw(self):
		if str(datetime.now().weekday()) == self.withdraw_weekday:
			self.data.update(
				action='TiXianToUserAlipay',
				amount = self.withdraw_amount,
				phone = self.phonenum,
				paytype = 'ALIPAY',
			)
			response = self.session.post(self.withdraw_url, data=self.data)
			return response

	def run(self):
		login_response = self.login()
		sigin_response = self.signin()
		browser_response = self.browser()
		withdraw_response = self.withdraw()
		return login_response, sigin_response, browser_response, withdraw_response

def main():
	adrobot = Adrobot()
	adrobot.run()

if __name__ == '__main__':
	main()
