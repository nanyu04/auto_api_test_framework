"""
【用户 Fixture 工厂】

共享的可复用 fixture，供多个测试模块使用。
"""
import pytest
from common import AssertionEngine
from apis import user_api
from data import factory
from utils import get_project_root, read_yaml

@pytest.fixture
def a_new_admin(logged_in_admin, context):
    """
    用管理员身份创建一个测试用户，测试结束自动删除

    创建用户走的是管理员接口，所以先依赖 logged_in_admin 完成登录。

    用法：
        def test_something(a_new_stu):
            user_id = a_new_stu["id"]
            # ... 对该用户进行操作
    """
    create_user_data=read_yaml(get_project_root() / "data/test_data/create_stu_admin.yaml")
    create_user_url=create_user_data[1]["url"]
    create_user_json=create_user_data[1]["request"]["json"]
    # userName 是学之思的字段名，必须显式指定，否则不打唯一后缀，重复执行会撞名
    payload = context.tag(create_user_json, ["userName"])

    resp=user_api.create_user(create_user_url, payload)
    ae = AssertionEngine(resp)
    ae.status_code(200).jsonpath_eq("$.code", 1)
    user_id = ae.extract("response.id")
    # 只有真正拿到 id 才登记清理，否则会去删 /delete/None
    if user_id:
        context.lifecycle.created("user", user_id)
    return {"id": user_id, "name": ae.extract("response.userName")}


@pytest.fixture
def logged_in_student():
    """
    用 student 账号登录，返回已带登录态的 user_api

    登录态由 Session 的 Cookie 保持，无需手动取 token。
    用法：
        def test_xxx(logged_in_student):
            resp = logged_in_student.get_user("/api/student/user/current")
    """
    login_data = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
    login_url = login_data[0]["url"]
    login_json = login_data[0]["request"]["json"]
    resp = user_api.login(login_url, login_json)
    AssertionEngine(resp).status_code(200).jsonpath_eq("$.code", 1)
    yield user_api
    user_api.client.clear_auth()
    user_api.client.session.cookies.clear()


@pytest.fixture
def logged_in_admin():
    """用 admin 账号登录，返回已带登录态的 user_api，用于后台管理类接口"""
    login_data = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
    login_url = login_data[1]["url"]
    login_json = login_data[1]["request"]["json"]
    resp = user_api.login(login_url, login_json)
    AssertionEngine(resp).status_code(200).jsonpath_eq("$.code", 1)
    yield user_api
    user_api.client.clear_auth()
    user_api.client.session.cookies.clear()
