"""
【断言引擎】 — 企业级响应验证工具

集成三种断言策略：
  1. 状态码 + 字段值 — 最常用
  2. JSON Schema — 契约验证
  3. DeepDiff — 全量/部分 JSON 比对

支持链式调用：assert_that(resp).status_code(200).jsonpath_eq("$.code", 0)
"""
from typing import Any, Optional
from deepdiff import DeepDiff
import jsonschema
from jsonpath_ng import parse as jsonpath_parse
from common.logger import logger


class AssertionEngine:
    """
    响应断言引擎

    用法：
        resp = client.get("/users/1")
        ae = AssertionEngine(resp)

        # 链式断言
        (ae
            .status_code(200)
            .jsonpath_eq("$.code", 0)
            .has_field("data.id")
            .schema(user_schema)
        )

        # 提取值供后续使用
        user_id = ae.extract("data.id")
    """

    def __init__(self, response):
        self._resp = response
        self._json_body: Any = None

    # ==================== 状态码断言 ====================

    def status_code(self, expected: int, message: str = "") -> "AssertionEngine":
        """断言 HTTP 状态码"""
        actual = self._resp.status_code
        assert actual == expected, (
            message or f"状态码断言失败: 期望 {expected}, 实际 {actual}"
        )
        logger.info(f"  ✓ 状态码 {expected}")
        return self

    # ==================== 全量 JSON 比对（DeepDiff） ====================

    def json_equal(self, expected: dict, exclude_paths: Optional[list] = None,
                   **kwargs) -> "AssertionEngine":
        """
        全量 JSON 相等校验

        参数：
            expected:        期望的完整 JSON
            exclude_paths:   忽略的字段列表，如 ["root['timestamp']"]
            kwargs:          DeepDiff 的其他参数
        """
        body = self._json
        #DeepDiff 是第三方库 deepdiff 提供的一个深度比对工具。作用是：把两个数据结构逐层、逐个字段地比一遍，把不同的地方都列出来。
        diff = DeepDiff(body, expected, exclude_paths=exclude_paths, **kwargs)
        if diff: #不是假  就是非空 就是有差异的意思
            logger.error(f"  ✗ JSON 不匹配:\n{diff.pretty()}")
            raise AssertionError(f"JSON 不匹配:\n{diff.pretty()}")
        logger.info("  ✓ 全量 JSON 校验通过")
        return self

    # ==================== 部分字段比对 ====================

    def json_contains(self, expected: dict, **kwargs) -> "AssertionEngine":
        """
        部分字段校验（只检查 expected 中出现的字段）

        常用于只关心几个关键字段，不关心其他字段的场景。
        """
        body = self._json
        subset = {k: body.get(k) for k in expected}
        diff = DeepDiff(subset, expected, **kwargs)
        if diff:
            logger.error(f"  ✗ 部分字段不匹配:\n{diff.pretty()}")
            raise AssertionError(f"部分字段不匹配:\n{diff.pretty()}")
        logger.info(f"  ✓ 字段校验通过: {list(expected.keys())}")
        return self

    # ==================== JSON Schema 校验 ====================

    def schema(self, schema_dict: dict) -> "AssertionEngine":

        """JSON Schema 契约校验
        例子  schema_dict例子
        API_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["code", "message"],
    "properties": {
        "code": {"type": "integer"},
        "message": {"type": "string"},
        "data": {},
    },"""
        try:
            jsonschema.validate(instance=self._json, schema=schema_dict)
        except jsonschema.ValidationError as e:
            logger.error(f"  ✗ Schema 校验失败:\n{e}")
            raise AssertionError(f"JSON Schema 校验失败:\n{e.message}")
        logger.info("  ✓ Schema 校验通过")
        return self

    # ==================== JSONPath 取值 + 断言 ====================

    def jsonpath(self, expr: str) -> Any:
        """
        JSONPath 表达式取值

        示例：
            "$.data.id"       → data 下的 id
            "$.items[0].name"  → 第一个 item 的 name
            "$..price"         → 所有层级的 price
        """
        matches = jsonpath_parse(expr).find(self._json)
        if not matches:
            logger.warning(f"  ⚠ JSONPath '{expr}' 未匹配到任何值")
            return None
        return matches[0].value

    def jsonpath_eq(self, expr: str, expected: Any) -> "AssertionEngine":
        """JSONPath 取值后断言相等"""
        actual = self.jsonpath(expr)
        assert actual == expected, (
            f"JSONPath '{expr}' 值不匹配: 期望 {expected}, 实际 {actual}"
        )
        logger.info(f"  ✓ {expr} == {expected}")
        return self

    # ==================== 字段存在性 ====================

    def has_field(self, field_path: str) -> "AssertionEngine":
        """
        断言字段存在（支持嵌套）

        ae.has_field("data.user.name")
        """
        keys = field_path.split(".")
        current = self._json
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                raise AssertionError(f"字段 '{field_path}' 不存在")
        logger.info(f"  ✓ 字段 '{field_path}' 存在")
        return self

    def not_has_field(self, field_path: str) -> "AssertionEngine":
        """断言字段不存在"""
        keys = field_path.split(".")
        current = self._json
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return self  # 不存在，断言成功
        raise AssertionError(f"字段 '{field_path}' 存在（预期不存在）")

    # ==================== 数组相关 ====================

    def array_length(self, expr: str, expected_len: int) -> "AssertionEngine":
        """断言数组长度"""
        arr = self.jsonpath(expr)
        assert isinstance(arr, list), f"JSONPath '{expr}' 不是数组"
        assert len(arr) == expected_len, (
            f"数组长度不匹配: 期望 {expected_len}, 实际 {len(arr)}"
        )
        logger.info(f"  ✓ 数组 '{expr}' 长度 == {expected_len}")
        return self

    # ==================== 值提取（供后续用例使用） ====================
    #这个field 就是 data.user.name  就相当于是哪一层哪一层这样子 要精准到键
    def extract(self, field: str, default: Any = None) -> Any:
        """
        从响应中提取字段值（点号分隔嵌套）

        用于用例间传参，如提取 user_id 供删除用例使用
        """
        keys = field.split(".")
        current = self._json
        for k in keys:
            if isinstance(current, dict):
                current = current.get(k, default)
            else:
                return default
        return current

    # ==================== 私有方法 ====================
    #
    @property
    def _json(self) -> Any:
        if self._json_body is None:
            try:
                self._json_body = self._resp.json()
            except Exception as e:
                raise ValueError(f"响应不是合法 JSON: {e}") from e
        return self._json_body

    # ==================== 语义别名（提高可读性） ====================

    ok = lambda self: self.status_code(200)
    created = lambda self: self.status_code(201)
    no_content = lambda self: self.status_code(204)
    bad_request = lambda self: self.status_code(400)
    unauthorized = lambda self: self.status_code(401)
    forbidden = lambda self: self.status_code(403)
    not_found = lambda self: self.status_code(404)
    server_error = lambda self: self.status_code(500)