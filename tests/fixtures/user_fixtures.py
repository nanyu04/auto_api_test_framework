"""
【用户 Fixture 工厂】

共享的可复用 fixture，供多个测试模块使用。
"""
import pytest
from common import AssertionEngine
from apis import user_api
from data import factory


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