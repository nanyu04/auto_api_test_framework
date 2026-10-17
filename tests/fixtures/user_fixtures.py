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
def a_new_user(context):
    """
    创建一个测试用户，自动清理

    用法：
        def test_something(a_new_user):
            user_id = a_new_user["id"]
            # ... 对该用户进行操作
    """
    payload = context.tag(factory.create_user_payload())
    resp = user_api.create(payload)
    ae = AssertionEngine(resp)
    ae.status_code(201)
    user_id = ae.extract("data.id")
    context.lifecycle.created("user", user_id)
    return {"id": user_id, "name": ae.extract("data.name")}


@pytest.fixture
def logged_in_student():
    """
    用 student 账号登录，返回已带登录态的 user_api

    用法：
        def test_xxx(logged_in_student):
            resp = logged_in_student.post("/api/student/dashboard/task")
    """
    login_data = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
    login_url = login_data[0]["url"]
    login_json = login_data[0]["request"]["json"]
    resp=user_api.login(login_url, login_json)
    token = AssertionEngine(resp).status_code(200).extract("token")  # Cookie 型接口取不到就跳过
    if token:
        user_api.client.set_token(token)
    yield user_api
    user_api.client.clear_auth()  # 清鉴权头
    user_api.client.session.cookies.clear()  # 清 Cookie，避免漏到下一个用例

@pytest.fixture
def logged_in_admin():
    #管理员登入
    login_data = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
    login_url = login_data[1]["url"]
    login_json = login_data[1]["request"]["json"]
    resp=user_api.login(login_url, login_json)
    token = AssertionEngine(resp).status_code(200).extract("token")  # Cookie 型接口取不到就跳过
    if token:
        user_api.client.set_token(token)
    yield user_api
    user_api.client.clear_auth()  # 清鉴权头
    user_api.client.session.cookies.clear()  # 清 Cookie，避免漏到下一个用例


# @pytest.fixture
