"""
【契约测试】— 自动从注册中心生成

这里不需要写具体的测试逻辑，
框架自动遍历 ContractRegistry 中注册的端点，
验证：
  1. Schema 自身合法性
  2. 所有 required 字段在 Schema 中有定义
"""
import pytest
from framework.contract import registry
import jsonschema


class TestContractSchema:
    """契约测试 — Schema 合法性验证"""

    @pytest.mark.contract
    def test_all_registered_schemas_are_valid(self):
        """所有注册的 Schema 自身必须是合法的 JSON Schema"""
        registrations = registry.find_all()
        assert len(registrations) > 0, "没有注册任何 Schema"

        for reg in registrations:
            if reg.response_schema:
                try:
                    # JSON Schema 自校验
                    jsonschema.Draft7Validator.check_schema(reg.response_schema)
                except Exception as e:
                    pytest.fail(f"Schema 不合法: {reg.description}\n  {e}")

    @pytest.mark.contract
    def test_required_fields_have_definitions(self):
        """required 字段必须在 properties 中有定义"""
        for reg in registry.find_all():
            schema = reg.response_schema
            if not schema:
                continue
            required = schema.get("required", [])
            props = schema.get("properties", {})
            for field in required:
                assert field in props, (
                    f"{reg.description}: required 字段 '{field}' "
                    f"在 properties 中未定义"
                )

    @pytest.mark.contract
    def test_coverage_summary(self):
        """打印注册覆盖率"""
        regs = registry.find_all()
        methods = set(r.method for r in regs)
        print(f"\n  已注册 {len(regs)} 个端点:")
        for r in regs:
            print(f"    {r.method:6s} {r.pattern:30s} {r.description}")
        print(f"  涉及 HTTP 方法: {', '.join(sorted(methods))}")
        assert len(regs) >= 5, (
            f"注册端点过少 ({len(regs)})，请检查 models/__init__.py 中的注册"
        )