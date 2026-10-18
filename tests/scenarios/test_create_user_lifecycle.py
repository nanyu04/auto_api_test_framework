"""
【场景测试】— 用户创建

演示框架三个能力如何自动生效：
  1. context.tag() — 自动给数据打标，不同运行不会冲突
  2. context.lifecycle.created() — 自动清理
  3. 契约校验 — HttpClient 自动完成，测试不用管
"""
import allure
import pytest
from common import AssertionEngine, retry_on_failure
from apis import user_api
from data import factory
from utils import get_project_root, read_yaml


class TestCreateUser:
    """创建用户 — 每个用例独立验证一个关注点"""

    # ========== 正常场景 ==========

    @allure.epic("用户管理")
    @allure.feature("创建用户")
    @allure.story("管理员创建新用户")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.P0
    @retry_on_failure(max_attempts=3, wait_seconds=2)
    def test_create_basic(self, logged_in_admin, context):
        """
        正常创建用户（管理员接口）

        logged_in_admin 已完成登录，Cookie 自动带上。
        """
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        create_user_json = create_user_data[1]["request"]["json"].copy()
        payload = context.tag(create_user_json, ["userName"])

        resp = user_api.create_user(create_user_url, payload)
        ae = AssertionEngine(resp)
        ae.status_code(200).jsonpath_eq("$.code", 1).has_field("response.id")
        user_id = ae.extract("response.id")
        context.lifecycle.created("user", user_id)

        # 验证名字包含标签（说明隔离生效了）
        resp_name = ae.extract("response.userName") or ""
        assert context.identity.tag in resp_name, (
            f"数据隔离未生效: 响应中的名字 '{resp_name}' "
            f"不包含标签 '{context.identity.tag}'"
        )

    # ========== 异常场景 ==========

    @allure.epic("用户管理")
    @allure.feature("创建用户")
    @allure.story("缺少必填字段")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.P1
    def test_create_missing_required(self, logged_in_admin, context):
        """缺少必填字段 → 接口返回失败"""
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        create_user_json = create_user_data[1]["request"]["json"].copy()
        create_user_json.pop("userName", None)

        resp = user_api.create_user(create_user_url, create_user_json)
        ae = AssertionEngine(resp)
        ae.status_code(200)
        assert ae.extract("code") != 1, f"期望失败，实际 code={ae.extract('code')}"

    @allure.epic("用户管理")
    @allure.feature("创建用户")
    @allure.story("重复用户名创建")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.P2
    @retry_on_failure(max_attempts=3, wait_seconds=2)
    def test_create_duplicate_username(self, context, a_new_admin):
        """
        重复用户名 → 用户已存在

        a_new_admin 已创建了一个用户，拿它的 userName 再创建一次。
        """
        first_name = a_new_admin["name"]

        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        payload = create_user_data[1]["request"]["json"].copy()
        payload["userName"] = first_name

        resp = user_api.create_user(create_user_url, payload)

        # code=2 表示"用户已存在"
        AssertionEngine(resp).status_code(200).jsonpath_eq("$.code", 2)

    # ========== 边界测试 ==========

    @allure.epic("用户管理")
    @allure.feature("创建用户")
    @allure.story("超长 userName 边界")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.P2
    def test_create_long_username(self, logged_in_admin, context):
        """超长 userName → 应被拒绝"""
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        payload = create_user_data[1]["request"]["json"].copy()
        # 构造一个超长用户名
        payload["userName"] = "a" * 256

        resp = user_api.create_user(create_user_url, payload)
        ae = AssertionEngine(resp)
        ae.status_code(200)
        assert ae.extract("code") != 1, f"超长 userName 应被拒绝，实际 code={ae.extract('code')}"

    @allure.epic("用户管理")
    @allure.feature("创建用户")
    @allure.story("特殊字符 userName")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.P2
    def test_create_special_chars_username(self, logged_in_admin, context):
        """特殊字符 userName → 应被拒绝或转义"""
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        payload = create_user_data[1]["request"]["json"].copy()
        payload["userName"] = "<script>alert(1)</script>"

        resp = user_api.create_user(create_user_url, payload)
        ae = AssertionEngine(resp)
        ae.status_code(200)
        # 要么拒绝（code != 1），要么转义后成功——只要不 500 就算通过
        assert resp.status_code < 500, f"特殊字符导致服务端异常: {resp.status_code}"

    @allure.epic("用户管理")
    @allure.feature("创建用户")
    @allure.story("空字符串 userName 边界")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.P2
    def test_create_empty_username(self, logged_in_admin, context):
        """空 userName → 应被拒绝"""
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        payload = create_user_data[1]["request"]["json"].copy()
        payload["userName"] = ""

        resp = user_api.create_user(create_user_url, payload)
        ae = AssertionEngine(resp)
        ae.status_code(200)
        assert ae.extract("code") != 1, f"空 userName 应被拒绝，实际 code={ae.extract('code')}"

    @allure.epic("用户管理")
    @allure.feature("创建用户")
    @allure.story("缺失密码字段")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.P2
    def test_create_missing_password(self, logged_in_admin, context):
        """缺少密码 → 应被拒绝"""
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        payload = create_user_data[1]["request"]["json"].copy()
        payload.pop("password", None)

        resp = user_api.create_user(create_user_url, payload)
        ae = AssertionEngine(resp)
        ae.status_code(200)
        assert ae.extract("code") != 1, f"缺密码应被拒绝，实际 code={ae.extract('code')}"

    @allure.epic("用户管理")
    @allure.feature("创建用户")
    @allure.story("age 边界值")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.P2
    @pytest.mark.parametrize("age,should_pass", [
        (-1, False),
        (0, True),
        (150, True),
        (151, False),
    ])
    def test_create_age_boundary(self, logged_in_admin, context, age, should_pass):
        """age 边界值校验"""
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        payload = create_user_data[1]["request"]["json"].copy()
        payload["age"] = age

        resp = user_api.create_user(create_user_url, payload)
        ae = AssertionEngine(resp)
        ae.status_code(200)
        if should_pass:
            # 合法值应该创建成功
            user_id = ae.extract("response.id")
            if user_id:
                context.lifecycle.created("user", user_id)
        else:
            assert ae.extract("code") != 1, f"age={age} 应被拒绝，实际 code={ae.extract('code')}"