"""
【接口层】— 鉴权模块 API 封装
"""
from common import BaseApi, HttpClient


class AuthApi(BaseApi):
    """用户鉴权接口"""

    service_path = ""

    def login(self, json_body: dict, **kwargs):
        """登录 """
        return self.post("/api/user/login", json=json_body, **kwargs)

    def logout(self):
        """登出"""
        return self.post("/api/user/logout")

    def signup(self,json_body,**kwargs):
        """注册"""
        return self.post("/api/student/user/register",json=json_body, **kwargs )



    def refresh_token(self, refresh_token: str, **kwargs):
        """刷新 Token → POST /api/v1/auth/refresh"""
        return self.post("/refresh", json={"refresh_token": refresh_token}, **kwargs)


auth_api = AuthApi()