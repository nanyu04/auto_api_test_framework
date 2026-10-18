"""
【场景测试】— 用户创建

演示框架三个能力如何自动生效：
  1. context.tag() — 自动给数据打标，不同运行不会冲突
  2. context.lifecycle.created() — 自动清理
  3. 契约校验 — HttpClient 自动完成，测试不用管
"""
import pytest
from common import AssertionEngine
from apis import user_api
from utils import get_project_root, read_yaml


class TestCreateUser:
    """创建用户 — 每个用例独立验证一个关注点"""

    @pytest.mark.smoke
    @pytest.mark.P0
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

    @pytest.mark.regression
    @pytest.mark.P1
    def test_create_missing_required(self, logged_in_admin, context):
        """缺少必填字段 → 400"""
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        create_user_json = create_user_data[1]["request"]["json"].copy()
        create_user_json.pop("userName", None)

        resp = user_api.create_user(create_user_url, create_user_json)
        # 这个接口所有情况都返回 200，错误通过 body.code 区分
        ae = AssertionEngine(resp)
        ae.status_code(200)
        assert ae.extract("code") != 1, f"期望失败，实际 code={ae.extract('code')}"

    @pytest.mark.regression
    @pytest.mark.P2
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