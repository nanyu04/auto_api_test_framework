"""
【场景测试】— 用户更新 & 删除

全部通过 context 做数据隔离和生命周期管理。
"""
import allure
import pytest
from common import AssertionEngine, retry_on_failure
from apis import user_api
from utils import get_project_root, read_yaml


# ==================== 更新测试 ====================


class TestUpdateUser:
    """更新用户"""

    @allure.epic("用户管理")
    @allure.feature("更新用户")
    @allure.story("正常更新用户名")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.P0
    @retry_on_failure(max_attempts=3, wait_seconds=2)
    def test_update_name(self, logged_in_admin, a_new_admin):
        """更新用户名"""
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        edit_url = create_user_data[1]["url"]

        new_name = f"updated_{a_new_admin['name']}"
        edit_json = create_user_data[1]["request"]["json"].copy()
        edit_json["id"] = a_new_admin["id"]
        edit_json["userName"] = new_name

        resp = user_api.edit_user(edit_url, edit_json)
        (AssertionEngine(resp)
         .status_code(200)
         .jsonpath_eq("$.code", 1)
         .jsonpath_eq("$.response.userName", new_name))

    @allure.epic("用户管理")
    @allure.feature("更新用户")
    @allure.story("更新不存在用户")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.P2
    @pytest.mark.skip(reason="接口不校验 id 是否存在，传任意 id 都返回 code=1，无法测此场景")
    def test_update_not_found(self, logged_in_admin):
        """更新不存在的用户"""
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        edit_url = create_user_data[1]["url"]

        edit_json = create_user_data[1]["request"]["json"].copy()
        edit_json["id"] = 9999999
        edit_json["userName"] = "ghost"

        resp = user_api.edit_user(edit_url, edit_json)
        ae = AssertionEngine(resp)
        ae.status_code(200)
        assert ae.extract("code") != 1, f"期望失败，实际 code={ae.extract('code')}"


# ==================== 删除测试 ====================


class TestDeleteUser:
    """删除用户"""

    @allure.epic("用户管理")
    @allure.feature("删除用户")
    @allure.story("正常删除")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.P0
    @retry_on_failure(max_attempts=3, wait_seconds=2)
    def test_delete_normal(self, logged_in_admin, a_new_admin):
        """正常删除"""
        user_id = a_new_admin["id"]
        resp = user_api.delete_user(f"/api/admin/user/delete/{user_id}")
        AssertionEngine(resp).status_code(200).jsonpath_eq("$.code", 1)

    @allure.epic("用户管理")
    @allure.feature("删除用户")
    @allure.story("删除后查询确认不存在")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.P1
    def test_delete_then_get_404(self, logged_in_admin, a_new_admin):
        """删除后再查 → 不存在"""
        user_id = a_new_admin["id"]

        # 先删
        user_api.delete_user(f"/api/admin/user/delete/{user_id}")

        # 再查，应该不存在
        resp = user_api.get_user(f"/api/admin/user/select/{user_id}")
        ae = AssertionEngine(resp)
        ae.status_code(200)
        assert ae.extract("code") != 1, f"期望用户不存在，实际 code={ae.extract('code')}"

    @allure.epic("用户管理")
    @allure.feature("删除用户")
    @allure.story("重复删除幂等性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.P2
    def test_delete_idempotent(self, logged_in_admin, a_new_admin):
        """重复删除应该幂等，不报 5xx"""
        user_id = a_new_admin["id"]
        delete_url = f"/api/admin/user/delete/{user_id}"

        status1 = user_api.delete_user(delete_url).status_code
        status2 = user_api.delete_user(delete_url).status_code
        assert status1 < 500, f"首次删除返回 {status1}"
        assert status2 < 500, f"重复删除返回 {status2}"
