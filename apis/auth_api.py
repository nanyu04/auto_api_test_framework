"""
【接口层】— 鉴权模块 API 封装
"""
from common import BaseApi, HttpClient


class AuthApi(BaseApi):
    """用户鉴权接口"""

    service_path = "/api/v1/auth"

    def login(self, json_body: dict, **kwargs):
        """登录 → POST /api/v1/auth/login"""
        return self.post("/login", json=json_body, **kwargs)

    def logout(self, **kwargs):
        """登出 → POST /api/v1/auth/logout"""
        return self.post("/logout", **kwargs)

    def refresh_token(self, refresh_token: str, **kwargs):
        """刷新 Token → POST /api/v1/auth/refresh"""
        return self.post("/refresh", json={"refresh_token": refresh_token}, **kwargs)


auth_api = AuthApi()