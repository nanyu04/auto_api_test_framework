"""
【接口层】— 鉴权模块 API 封装
"""
from common import BaseApi, HttpClient


class AuthApi(BaseApi):
    """用户鉴权接口"""

    service_path = ""

    def login(self, url,json_body: dict, **kwargs):
        """登录 """
        return self.post(path=url, json=json_body, **kwargs)

    def logout(self,url):
        """登出"""
        return self.post(path=url)

    def signup(self,url,json_body,**kwargs):
        """注册"""
        return self.post(path=url,json=json_body, **kwargs )



    def refresh_token(self, url,refresh_token: str, **kwargs):
        """刷新 Token"""
        return self.post(path=url, json={"refresh_token": refresh_token}, **kwargs)


auth_api = AuthApi()