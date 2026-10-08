"""
【API 基类】 — 所有业务接口模块的父类

子类只需要定义 service_path，即可继承请求方法和验证器。
"""
from typing import Optional
from common.http_client import HttpClient
from common.logger import logger


class BaseApi:
    """
    API 基类

    用法：
        class UserApi(BaseApi):
            service_path = "/api/v1/users"

            def get_user(self, user_id):
                return self.get(str(user_id))

        api = UserApi()
        resp = api.get_user(1)
    """

    # 子类覆盖：接口路径前缀，如 "/api/v1/users"
    service_path: str = ""

    def __init__(self, client: Optional[HttpClient] = None):
        self.client = client or HttpClient()
        self.logger = logger

    # -------------------- 路径拼接 --------------------

    def _url(self, path: str = "") -> str:
        """拼接 service_path + path"""
        base = self.service_path.strip("/")
        path = path.strip("/")
        if base and path:
            return f"/{base}/{path}"
        return f"/{base}{path}" if base else path

    # -------------------- HTTP 方法快捷调用 --------------------

    def get(self, path: str = "", **kwargs):
        return self.client.get(self._url(path), **kwargs)

    def post(self, path: str = "", **kwargs):
        return self.client.post(self._url(path), **kwargs)

    def put(self, path: str = "", **kwargs):
        return self.client.put(self._url(path), **kwargs)

    def patch(self, path: str = "", **kwargs):
        return self.client.patch(self._url(path), **kwargs)

    def delete(self, path: str = "", **kwargs):
        return self.client.delete(self._url(path), **kwargs)