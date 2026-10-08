"""
【接口层】— 用户模块 API 封装

每个接口方法返回 requests.Response（原始响应），
测试用例中通过 AssertionEngine 进行链式断言。
"""
from common import BaseApi, HttpClient
from typing import Optional


class UserApi(BaseApi):
    """用户管理接口"""

    service_path = ""

    def create_user(self, json_body: dict, **kwargs):
        """创建用户 """
        return self.post(json=json_body, **kwargs)

    def get_user(self, user_id: int, **kwargs):
        """查询用户 """
        return self.post(str(user_id), **kwargs)
    def user_list(self, params: Optional[dict] = None, **kwargs):
        """用户列表 """
        return self.get(params=params, **kwargs)

    def update_user(self, user_id: int, json_body: dict, **kwargs):
        """更新用户"""
        return self.put(str(user_id), json=json_body, **kwargs)

    def delete_user(self, user_id: int, **kwargs):
        """删除用户 → DELETE /api/v1/users/{id}"""
        return self.delete(str(user_id), **kwargs)


# 全局单例
user_api = UserApi()