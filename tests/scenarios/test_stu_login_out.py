"""
【场景测试】— 登录 & 登出
"""
import allure
import pytest
from common import logger, AssertionEngine
from apis import auth_api
from utils import get_project_root, read_yaml


class TestLogin:
    @allure.epic("鉴权模块")
    @allure.feature("用户登录")
    @allure.story("多账号登录验证")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.P0
    def test_login_with_multiple_users(self, context):
        """验证多个账号都能登录成功，分别断言每个账号的结果"""
        login_data = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
        results = []
        for k in login_data:
            login_param = k["request"]["json"]
            login_path = k["url"]
            resp = auth_api.login(login_path, login_param)
            ae = AssertionEngine(resp)
            ae.status_code(200).jsonpath_eq("$.code", 1)

            user_name = ae.extract("response.userName")
            assert user_name, (
                f"登录响应缺少 response.userName —— "
                f"账号 {login_param.get('userName')} 可能登录失败: {resp.text}"
            )
            results.append({"userName": user_name, "status": "OK"})
            logger.info(f"  ✓ {login_param['userName']} 登录成功 → {user_name}")

        assert len(results) == len(login_data), (
            f"期望 {len(login_data)} 个账号全部成功，实际 {len(results)} 个"
        )


class TestLogout:
    @allure.epic("鉴权模块")
    @allure.feature("用户登出")
    @allure.story("先登录后登出")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.P0
    def test_logout_success(self, context):
        """先登录再登出，验证登出成功"""
        login_data = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
        for k in login_data:
            user_name = k["request"]["json"]["userName"]
            auth_api.login("/api/user/login", k["request"]["json"])
            resp = auth_api.logout(url="/api/user/logout")
            ae = AssertionEngine(resp)
            ae.status_code(200).jsonpath_eq("$.code", 1)
            logger.info(f"  ✓ {user_name} 登出成功")