"""
【接口层】— 用户模块 API 封装

每个接口方法返回 requests.Response（原始响应），
测试用例中通过 AssertionEngine 进行链式断言。
"""
from common import BaseApi, HttpClient
from typing import Optional


class UserApi(BaseApi):
    """用户管理接口"""

    service_path = "/api/v1/users"

    def create(self, json_body: dict, **kwargs):
        """创建用户 → POST /api/v1/users"""
        return self.post(json=json_body, **kwargs)

    def get(self, user_id: int, **kwargs):
        """查询用户 → GET /api/v1/users/{id}"""
        return super().get(str(user_id), **kwargs)

    def list(self, params: Optional[dict] = None, **kwargs):
        """用户列表 → GET /api/v1/users"""
        return super().get(params=params or {}, **kwargs)

    def update(self, user_id: int, json_body: dict, **kwargs):
        """更新用户 → PUT /api/v1/users/{id}"""
        return self.put(str(user_id), json=json_body, **kwargs)

    def delete(self, user_id: int, **kwargs):
        """删除用户 → DELETE /api/v1/users/{id}"""
        return super().delete(str(user_id), **kwargs)


# 全局单例
user_api = UserApi()