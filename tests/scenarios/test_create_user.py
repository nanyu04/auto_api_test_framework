# """
# 【场景测试】— 用户创建
#
# 演示框架三个能力如何自动生效：
#   1. context.tag() — 自动给数据打标，不同运行不会冲突
#   2. context.lifecycle.created() — 自动清理
#   3. 契约校验 — HttpClient 自动完成，测试不用管
# """
# import pytest
# from common import AssertionEngine
# from apis import user_api
# from data import factory
#
#
# class TestCreateUser:
#     """创建用户 — 每个用例独立验证一个关注点"""
#
#     @pytest.mark.smoke
#     @pytest.mark.P0
#     def test_create_basic(self, context, api_client):
#         """
#         正常创建用户
#
#         框架做了什么（测试不用管）：
#           ✅ context 给数据打上了唯一标签 → 不会跟其他运行冲突
#           ✅ 响应自动经契约校验 → 结构不符合 Schema 会告警
#           ✅ lifecyle.created() 注册 → 测试结束自动清理
#         """
#         # Given: 准备测试数据（自动打标，确保隔离）
#         payload = context.tag(factory.create_user_payload())
#         # payload 中的 name/email 会被自动加上唯一前缀
#
#         # When: 创建用户
#         resp = user_api.create(payload)
#
#         # Then: 验证结果
#         ae = AssertionEngine(resp)
#         ae.status_code(201).jsonpath_eq("$.code", 0).has_field("data.id")
#
#         # ✅ 注册清理（teardown 自动执行）
#         user_id = ae.extract("data.id")
#         context.lifecycle.created("user", user_id)
#
#         # 验证名字包含标签（说明隔离生效了）
#         resp_name = ae.extract("data.name") or ""
#         assert context.identity.tag in resp_name, (
#             f"数据隔离未生效: 响应中的名字 '{resp_name}' "
#             f"不包含标签 '{context.identity.tag}'"
#         )
#
#     @pytest.mark.regression
#     @pytest.mark.P1
#     def test_create_missing_required(self, context):
#         """缺少必填字段 → 400"""
#         payload = factory.create_user_payload()
#         payload.pop("name", None)
#
#         resp = user_api.create(payload)
#         AssertionEngine(resp).status_code(400)
#         # 注意：这个测试没有创建数据，所以不需要生命周期管理
#
#     @pytest.mark.regression
#     @pytest.mark.P2
#     @pytest.mark.parametrize("field,value,desc", [
#         ("name", "", "空字符串"),
#         ("email", "not-email", "无效格式"),
#         ("age", -1, "负数"),
#         ("age", 200, "超龄"),
#     ])
#     def test_create_invalid_fields(self, context, field, value, desc):
#         """无效字段值（参数化数据驱动）"""
#         payload = factory.create_user_payload()
#         payload[field] = value
#
#         resp = user_api.create(payload)
#         AssertionEngine(resp).status_code(400)
#
#     @pytest.mark.regression
#     @pytest.mark.P2
#     def test_create_duplicate_email(self, context):
#         """
#         重复邮箱 → 409
#
#         一个测试内完成"准备 → 操作 → 验证 → 清理"的闭环。
#         """
#         # Given: 先用固定邮箱创建一个用户
#         email = f"dup_{context.identity.tag}@test.com"
#         payload = context.tag(factory.create_user_payload(email=email))
#
#         resp = user_api.create(payload)
#         ae = AssertionEngine(resp)
#         ae.status_code(201)
#         first_id = ae.extract("data.id")
#         context.lifecycle.created("user", first_id)
#
#         # When: 相同邮箱再创建
#         resp = user_api.create(payload)
#
#         # Then: 应该冲突
#         AssertionEngine(resp).status_code(409)