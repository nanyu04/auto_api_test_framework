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
    def login(self, url,json_body: dict, **kwargs):
        """登录 """
        return self.post(path=url, json=json_body, **kwargs)

    def create_user(self, url,json_body: dict, **kwargs):
        """创建用户 """
        return self.post(path=url,json=json_body, **kwargs)
    def edit_user(self, url,json_body: dict, **kwargs):
        """修改用户信息 """
        return self.post(path=url, json=json_body, **kwargs)

    def get_user(self,url, **kwargs):
        """查询用户 """
        return self.post(path=url, **kwargs)
    def user_list(self, url,params: Optional[dict] = None, **kwargs):
        """用户列表 """
        return self.get(path=url,params=params, **kwargs)

    def update_user(self,url,  json_body: dict, **kwargs):
        """更新用户"""
        return self.put(path=url, json=json_body, **kwargs)

    def delete_user(self, url, **kwargs):
        """删除用户"""
        return self.delete(path=url, **kwargs)


# 全局单例
user_api = UserApi()