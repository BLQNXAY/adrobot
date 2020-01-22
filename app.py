import os
import sys
import time
import random
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from requests import Session

class Adrobot:
    code_url = 'http://www.5iads.cn/module/user/code.asp'
    login_url = 'http://www.5iads.cn/module/user/login.asp'
    sgin_url = 'http://www.5iads.cn/module/user/Signin.asp'
    ad_url = 'http://www.5iads.cn/module/dianji/'
    surf_url = 'http://www.5iads.cn/module/surf/'
    check_url = 'http://www.5iads.cn/module/' 
    withdraw_url = 'http://www.5iads.cn/module/user/tixian.asp'

    def __init__(self):
        load_dotenv(find_dotenv())
        self.username = os.environ.get('username')
        self.password = os.environ.get('password')

        self.session = Session()
        self.session.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'www.5iads.cn',
            'Origin': 'http://www.5iads.cn',
            'Referer': 'http://www.5iads.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
    }

    def __del__(self):
        self.session.close()

    def _refresh_code(self):
        for _ in range(30):
            response = self.session.get(self.code_url)
            if response.text == 'http://www.5iads.cn/yzmfile/7.jpg|/t.asp?id=7|success':
                return True
        return False

    def login(self):
        if self._refresh_code():
            login_data = {
                'action': 'loginsys',
                'Username': self.username,
                'Password': self.password,
                'checkcode': '50'
            }
            response = self.session.post(self.login_url, data=login_data)
            return response
        else:
            print('Default login')
            sys.exit()

    def sgin(self):
        response = self.session.get(self.sgin_url, params=dict(action='signin'))
        return response

    def _get_ads(self):
        ads_data = {
            'action': 'loadDianjiList',
            'row': '20',
            'pagenum': '1'
        }
        response = self.session.post(self.ad_url, data=ads_data)
        ads = [ad['id'] for ad in response.json()]
        return ads

    def _click_ad(self, ad_id):
        ad_data ={
            'Isjiami': 'false',
            'clickid': ad_id,
            'action': 'Show_dianji_getone',
        }
        response = self.session.post(self.ad_url, data=ad_data)
        return response.json()

    @staticmethod
    def _wait_ad(ad_info):
        time.sleep(7 + ad_info.get('miao', 20))

    def _finish_ad(self, ad_info):
        finish_data = {
            'action': ad_info['action'],
            'firstCk': 2,
            'YzmCheck': 'success',
            'clickid': ad_info['id'],
            'refurl': 'http://www.5iads.cn/reclick.asp?gourl=http://www.5iads.cn/zhuan.asp?zhuan=dianji',
            'sign': ad_info['sign'],
            'Isjiami': True,
            'key': random.random()
        }
        response = self.session.post(ad_url, data=finish_data)
        return response.text

    def browse(self):
        ads = self._get_ads()
        for ad in ads:
            ad_info = self._click_ad(ad)
            self._wait_ad(ad_info)
            self._finish_ad(ad_info)
    
    def _start_surf(self):
        start_surf_data = {
            'des': 'start',
            'type': 1,
            'manual': 0,
            'info': 'window_1',
            'timeB': int(datetime.now().timestamp()),
            'timeE': int(datetime.now().timestamp()),
	}
        response = self.session.post(self.surf_url, data=start_surf_data)
        surf_info = response.json()
        return surf_info

    @staticmethod
    def _wait_surf(interval=20):
        time.sleep(interval)

    def _finish_surf(self, surf_info):
        finish_surf_data = {
            'des': 'complete',
            'type': 1,
            'manual': 0,
            'info': 'window_1',
            'sign': surf_info['sign'],
            'timeB': int(datetime.now().timestamp()),
            'timeE': int(datetime.now().timestamp()),
            'id': surf_info['id'],
	}
        response = self.session.post(self.surf_url, data=finish_surf_data)
        return response

    def surf(self):
        surf_info = self._start_surf()
        self._wait_surf()
        response = self._finish_surf(surf_info)
        return response

    def _withdraw_headers(self):
        self.session.headers['Referer'] = 'http://www.5iads.cn/tixian.asp?agree=1'
        return self.session.headers

    def _check_user(self):
        response = self.session.post(self.check_url, data=dict(action='CheckUserLogin'))
        return response

    def _finish_check(self):
        response = self.session.post(self.check_url, data=dict(action='taskfinish'))
        return response

    def _start_withdraw(self):
        withdraw_data = {
            'amount': '2000',
            'tbuserpwd': '18269874870',
            'act': 'tixian'
        }
        response = self.session.post(self.withdraw_url, data=withdraw_data)
        return response

    def withdraw(self):
        if datetime.now().weekday() == 1:
            self._withdraw_headers()
            self._check_user()
            self._finish_check()
            response = self._start_withdraw()
            return response

    def run(self):
        self.login()
        self.sgin()
        self.browse()
        self.withdraw()

def main():
    adrobot = Adrobot()
    adrobot.run()

if __name__ == '__main__':
    main()
