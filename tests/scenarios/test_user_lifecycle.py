from apis import user_api
from common import logger, AssertionEngine
from utils import read_yaml, get_project_root


class TestCreateLifecycle:
    def test_create_lifecycle(self, logged_in_admin, context):
        """
        用管理员身份创建一个测试用户，测试结束自动删除

        创建用户走的是管理员接口，所以先依赖 logged_in_admin 完成登录。

        用法：
            def test_something(a_new_stu):
                user_id = a_new_stu["id"]
                # ... 对该用户进行操作
        """
        logger.info("---------------------开始进行用户创建标记操作--------------------")
        create_user_data = read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
        create_user_url = create_user_data[1]["url"]
        create_user_json = create_user_data[1]["request"]["json"]
        # userName 是学之思的字段名，必须显式指定，否则不打唯一后缀，重复执行会撞名
        payload = context.tag(create_user_json, ["userName"])
        resp = user_api.create_user(create_user_url, payload)
        ae = AssertionEngine(resp)
        ae.status_code(200).jsonpath_eq("$.code",1).has_field("response.id")
        user_id = ae.extract("response.id")
        assert user_id, f"创建成功了却没拿到 id —— 响应: {resp.text}"
        logger.info("----------------------开始查询用户是否正常创建------------------")
        check_user_alive = user_api.get_user(f"/api/admin/user/select/{user_id}")
        AssertionEngine(check_user_alive).status_code(200).jsonpath_eq("$.code",1)
        logger.info("----------------------开始添加进用户数据管理中心里面---------")
        context.lifecycle.created("user", user_id)

