"""
【场景测试】— 学生查看 & 编辑个人信息
"""
import allure
import pytest
from apis import user_api
from common import logger, AssertionEngine
from utils import read_yaml, get_project_root


class TestUserCheck:
    @allure.epic("用户管理")
    @allure.feature("学生信息")
    @allure.story("查看当前用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P0
    @pytest.mark.smoke
    def test_user_Check(self, logged_in_student):
        """查看当前登录用户信息：接口成功且返回正确数据"""
        logger.info("———————— 已登录，开始查询当前用户 ————————")
        current_info_url = "/api/student/user/current"
        resp = logged_in_student.get_user(current_info_url)
        (AssertionEngine(resp)
            .status_code(200)
            .jsonpath_eq("$.code", 1)
            .has_field("response"))
        user_name = AssertionEngine(resp).extract("response.userName")
        logger.info(f"  ✓ 当前用户: {user_name}")


class TestUserEdit:
    @allure.epic("用户管理")
    @allure.feature("学生信息")
    @allure.story("编辑个人信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P0
    @pytest.mark.smoke
    def test_user_edit(self, logged_in_student):
        """编辑个人信息：请求真实接口，验证返回 code=1"""
        edit_data = read_yaml(get_project_root() / "data/test_data/stu_update_info.yaml")
        edit_url = edit_data[0]["url"]
        edit_json = edit_data[0]["request"]["json"]
        resp = logged_in_student.edit_user(edit_url, edit_json)
        (AssertionEngine(resp)
            .status_code(200)
            .jsonpath_eq("$.code", 1))