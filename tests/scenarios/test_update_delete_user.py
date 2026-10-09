# """
# 【场景测试】— 用户更新 & 删除
#
# 全部通过 context 做数据隔离和生命周期管理。
# """
# import pytest
# from common import AssertionEngine
# from apis import user_api
# from data import factory
#
#
# # ==================== 模块内共享 Fixture ====================
#
#
# @pytest.fixture
# def a_new_user(context):
#     """
#     创建一个测试用户
#
#     返回用户信息，测试结束后自动清理。
#     每次调用都创建新的用户，互不干扰。
#     """
#     payload = context.tag(factory.create_user_payload())
#     resp = user_api.create(payload)
#     ae = AssertionEngine(resp)
#     ae.status_code(201)
#     user_id = ae.extract("data.id")
#     user_name = ae.extract("data.name")
#
#     context.lifecycle.created("user", user_id)
#     return {"id": user_id, "name": user_name}
#
#
# # ==================== 更新测试 ====================
#
#
# class TestUpdateUser:
#     """更新用户"""
#
#     @pytest.mark.smoke
#     @pytest.mark.P0
#     def test_update_name(self, a_new_user):
#         """更新用户名"""
#         new_name = f"updated_{a_new_user['id']}"
#         resp = user_api.update(a_new_user["id"], {"name": new_name})
#         (AssertionEngine(resp)
#             .status_code(200)
#             .jsonpath_eq("$.data.name", new_name))
#
#     @pytest.mark.regression
#     @pytest.mark.P2
#     def test_update_not_found(self):
#         """更新不存在的用户"""
#         resp = user_api.update(9999999, {"name": "ghost"})
#         AssertionEngine(resp).status_code(404)
#
#
# # ==================== 删除测试 ====================
#
#
# class TestDeleteUser:
#     """删除用户"""
#
#     @pytest.mark.smoke
#     @pytest.mark.P0
#     def test_delete_normal(self, context):
#         """正常删除"""
#         payload = context.tag(factory.create_user_payload())
#         resp = user_api.create(payload)
#         ae = AssertionEngine(resp)
#         ae.status_code(201)
#         user_id = ae.extract("data.id")
#         context.lifecycle.created("user", user_id)
#
#         resp = user_api.delete(user_id)
#         AssertionEngine(resp).status_code(204)
#
#     @pytest.mark.regression
#     @pytest.mark.P1
#     def test_delete_then_get_404(self, context):
#         """删除后再查 → 404（在同一个测试内完成）"""
#         payload = context.tag(factory.create_user_payload())
#         resp = user_api.create(payload)
#         ae = AssertionEngine(resp)
#         ae.status_code(201)
#         user_id = ae.extract("data.id")
#         context.lifecycle.created("user", user_id)
#
#         user_api.delete(user_id)
#         resp = user_api.get(user_id)
#         AssertionEngine(resp).status_code(404)
#
#     @pytest.mark.regression
#     @pytest.mark.P2
#     def test_delete_idempotent(self, context):
#         """重复删除应该幂等，不报 5xx"""
#         payload = context.tag(factory.create_user_payload())
#         resp = user_api.create(payload)
#         ae = AssertionEngine(resp)
#         ae.status_code(201)
#         user_id = ae.extract("data.id")
#         context.lifecycle.created("user", user_id)
#
#         status1 = user_api.delete(user_id).status_code
#         status2 = user_api.delete(user_id).status_code
#         assert status1 < 500, f"首次删除返回 {status1}"
#         assert status2 < 500, f"重复删除返回 {status2}"