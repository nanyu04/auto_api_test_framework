from openai import responses
from common import logger, AssertionEngine

import pytest
from apis import auth_api, user_api
from utils import get_project_root, read_yaml


class TestLogin:
    @pytest.mark.smoke
    @pytest.mark.P0
    def test_login_with_multiple_users(self, context):
        """验证多个账号都能登录成功"""
        login_data = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
        for k in login_data:
            login_param = k["request"]["json"]
            login_path = k["url"]
            login_result = auth_api.login(login_path, login_param)
            ae = AssertionEngine(login_result)
            ae.status_code(200).has_field("message")


class TestLogout:
    @pytest.mark.smoke
    @pytest.mark.P0
    def test_logout_success(self, context):
        """先登录再登出，验证登出成功"""
        login_data = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
        for k in login_data:
            auth_api.login("/api/user/login", k["request"]["json"])
            logout_result = auth_api.logout(url="/api/user/logout")
            ae = AssertionEngine(logout_result)
            ae.status_code(200).has_field("message").has_field("response")

