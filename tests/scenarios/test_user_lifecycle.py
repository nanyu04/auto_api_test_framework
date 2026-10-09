# """
# 【场景测试】— 用户全生命周期（冒烟测试）
#
# 一个测试内完成创建 → 查询 → 更新 → 查询 → 删除 → 验证删除。
# 覆盖核心业务流程，不依赖任何外部状态。
# """
# import pytest
# from common import AssertionEngine, logger
# from apis import user_api
# from data import factory
#
#
# @pytest.mark.smoke
# @pytest.mark.P0
# def test_user_full_lifecycle(context):
#     """
#     用户完整生命周期
#
#     这个测试在 CI 中被标记为 smoke + P0，
#     每次部署前必跑。
#     """
#     # ===== Phase 1: 准备 & 创建 =====
#     payload = context.tag(factory.create_user_payload())
#     logger.info(f"  创建用户: name={payload.get('name')}")
#
#     resp = user_api.create(payload)
#     ae = AssertionEngine(resp)
#     ae.status_code(201).jsonpath_eq("$.code", 0).has_field("data.id")
#     user_id = ae.extract("data.id")
#     context.lifecycle.created("user", user_id)
#
#     # ===== Phase 2: 查询 =====
#     resp = user_api.get(user_id)
#     (AssertionEngine(resp)
#         .status_code(200)
#         .jsonpath_eq("$.data.id", user_id))
#
#     # ===== Phase 3: 更新 =====
#     new_name = f"updated_{user_id}"
#     resp = user_api.update(user_id, {"name": new_name})
#     AssertionEngine(resp).status_code(200)
#
#     # ===== Phase 4: 验证更新已生效 =====
#     resp = user_api.get(user_id)
#     (AssertionEngine(resp)
#         .status_code(200)
#         .jsonpath_eq("$.data.name", new_name))
#
#     # ===== Phase 5: 删除 =====
#     resp = user_api.delete(user_id)
#     AssertionEngine(resp).status_code(204)
#
#     # ===== Phase 6: 验证删除 =====
#     resp = user_api.get(user_id)
#     AssertionEngine(resp).status_code(404)
#
#     logger.info("  ✅ 全生命周期通过")