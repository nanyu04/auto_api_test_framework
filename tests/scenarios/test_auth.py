"""
【场景测试】— 鉴权

演示 mock 模式：在不依赖真实认证服务的情况下运行。
"""
import pytest
from common import AssertionEngine
from data import factory


class TestAuth:
    """鉴权测试"""

    @pytest.mark.smoke
    @pytest.mark.P0
    def test_login_and_use(self, context, api_client):
        """登录 → 获取 token → 访问受保护接口"""
        payload = factory.login_payload(
            username="admin",
            password="correct_password",
        )
        # TODO: 按实际接口调整 URL
        resp = api_client.post("/api/v1/auth/login", json=payload)
        ae = AssertionEngine(resp)
        ae.status_code(200).has_field("token")

        token = ae.extract("token")
        api_client.set_token(token)

        resp = api_client.get("/api/v1/users/me")
        AssertionEngine(resp).status_code(200)

    @pytest.mark.regression
    @pytest.mark.P1
    def test_wrong_password(self, api_client):
        payload = factory.login_payload(username="admin", password="wrong")
        resp = api_client.post("/api/v1/auth/login", json=payload)
        AssertionEngine(resp).status_code(401)

    @pytest.mark.regression
    @pytest.mark.P1
    def test_no_token(self, api_client):
        api_client.clear_auth()
        resp = api_client.get("/api/v1/users")
        AssertionEngine(resp).status_code(401)