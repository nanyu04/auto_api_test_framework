"""
【场景测试】— 用户生命周期

创建 → 查询 → 登记清理，完整闭环。
"""
import allure
from apis import user_api
from common import logger, AssertionEngine
from utils import read_yaml, get_project_root


@allure.epic("用户管理")
@allure.feature("用户生命周期")

class TestCreateLifecycle:
    @allure.story("创建用户完整生命周期")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_lifecycle(self, logged_in_admin, context):
        """
        用管理员身份创建一个测试用户，测试结束自动删除

        流程：创建 → 查询确认存在 → 登记生命周期 → 框架自动清理
        """
        logger.info("---------------------开始进行用户创建标记操作--------------------")
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        create_user_json = create_user_data[1]["request"]["json"]
        payload = context.tag(create_user_json, ["userName"])

        resp = user_api.create_user(create_user_url, payload)
        ae = AssertionEngine(resp)
        ae.status_code(200).jsonpath_eq("$.code", 1).has_field("response.id")
        user_id = ae.extract("response.id")
        assert user_id, f"创建成功了却没拿到 id —— 响应: {resp.text}"

        logger.info("----------------------开始查询用户是否正常创建------------------")
        check_user = user_api.get_user(f"/api/admin/user/select/{user_id}")
        AssertionEngine(check_user).status_code(200).jsonpath_eq("$.code", 1)

        logger.info("----------------------登记生命周期，测试结束自动清理---------")
        context.lifecycle.created("user", user_id)