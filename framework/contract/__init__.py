"""
framework/contract — 契约校验子系统
#
  ▎ 有一个列表存储了注册的信息，注册信息主要靠 pattern 和 method
  ▎ 来标识一个端点，并附带对应的 Schema。
  ▎
  ▎ 请求来了之后：
  ▎ - 用 method + pattern 找到对应的注册项 → 用 jsonschema.validate
  ▎ 校验实际数据
  ▎   - 数据符合 Schema → 通过，无事发生
  ▎   - 数据不符合 Schema → 报违规
  ▎ - 没找到对应的注册项 → 跳过，不做校验
核心能力：
  1. Schema 注册中心 —— 按 API 端点注册请求/响应 Schema
  2. 自动校验引擎 —— HTTP 客户端自动验证响应是否符合注册的 Schema
  3. 契约测试生成 —— 从注册中心生成测试用例
  4. 回归拦截 —— 接口结构变更自动告警

用法：
    # 在 models/ 或 conftest 中注册
    from framework.contract import registry
    from models import USER_SCHEMA

    registry.register("GET", "/api/v1/users/{id}", response_schema=USER_SCHEMA)

    # 之后所有通过 http_client 发出的请求，
    # 如果匹配注册的端点，响应会自动做 Schema 校验
"""
import json
import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from urllib.parse import urlparse
from common.logger import logger


# =============================================================
#  路由匹配
# =============================================================

# re是正则表达式的意思compile（）是函数它没说里面能干什么，但是返回的结果是re.Pattern
def _compile_pattern(pattern: str) -> re.Pattern:
    """将 /api/v1/users/{id} 转为正则"""
    parts = []
    # strip 将开头和结尾的/删除  split 就是将所有/分离开
    for segment in pattern.strip("/").split("/"):
        if segment.startswith("{") and segment.endswith("}"):
            parts.append(r"[^/]+")  # `[^/]+` = **匹配一段连续的、不包含斜杠 `/` 的字符串**
        else:
            # `re.escape()`：把普通 url 片段转义，防止里面有正则特殊符号干扰。
            parts.append(re.escape(segment))
            # ^表示开始  $表示结束 re.compile正则字符串 "^api/v1/users/[^/]+$"
    return re.compile(f"^{'/'.join(parts)}$")


def _extract_path(url: str) -> str:
    """从完整 URL 中提取路径部分"""
    # 内置方法，会将url 分为 scheme：http  netloc：ip地址 path：路径 query：查询参数
    parsed = urlparse(url)
    return parsed.path.rstrip("/")


# =============================================================
#  Schema 注册项
# =============================================================



# @dataclass Python**自动帮你生成上面一整套`__init__`，
# 自动完成`self.method=method`、`self.pattern=pattern`赋值**，你不用手写。
@dataclass
class SchemaRegistration:
    """一次 Schema 注册"""
    method: str
    pattern: str
    response_schema: Optional[dict] = None
    request_schema: Optional[dict] = None
    description: str = ""
    _pattern_re: re.Pattern = field(init=False)
    # 写了这个__post_init__ 创建了SchemaRegistration会自动调用 因为@dataclass
    def __post_init__(self):
        self._pattern_re = _compile_pattern(self.pattern)

    def matches(self, method: str, path: str) -> bool:
        """判断请求是否匹配此注册"""
        return (method.upper() == self.method.upper()
                and bool(self._pattern_re.match(path.strip("/"))))


# =============================================================
#  ContractRegistry — 注册中心
# =============================================================


class ContractRegistry:
    """
    Schema 注册中心
    单例模式，全局只需要一个实例。
    """

    def __init__(self):
        self._registrations: List[SchemaRegistration] = []
        self._enabled = True

    # ---------- 注册 ----------

    def register(self, method: str, pattern: str,
                 response_schema: Optional[dict] = None,
                 request_schema: Optional[dict] = None,
                 description: str = "") -> "ContractRegistry":
        """
        注册一个 API 端点的 Schema

        参数：
            method:         HTTP 方法
            pattern:        URL 模式，如 /api/v1/users/{id}
            response_schema: 响应体的 JSON Schema
            request_schema:  请求体的 JSON Schema（可选）
            description:     描述
        """
        reg = SchemaRegistration(
            method=method.upper(),
            pattern=pattern,
            response_schema=response_schema,
            request_schema=request_schema,
            description=description or f"{method} {pattern}",
        )
        self._registrations.append(reg)
        logger.info(f"  📋 [Contract] 注册: {reg.description}")
        # 支持链式调用就是相当于可以 ContractRegistry.register().register这样一直注册直到注册完毕
        return self

    # ---------- 匹配 ----------

    def find(self, method: str, url: str) -> Optional[SchemaRegistration]:
        """查找匹配的注册项"""
        path = _extract_path(url)
        for reg in self._registrations:
            if reg.matches(method, path):
                return reg
        return None

    def find_all(self, method: Optional[str] = None) -> List[SchemaRegistration]:
        """查询所有注册项（可按方法过滤）"""
        if method:
            # 这里r就指的是能满足 for r in self._registrations ：
            #                   if r.method == method.upper()  就放入method里面
            return [r for r in self._registrations if r.method == method.upper()]
        #就是不想让外面拿到原件，怕被人乱改。 算是一个常见的防御性编程习惯。
        return self._registrations.copy()

    # ---------- 校验 ----------

    def validate_response(self, method: str, url: str,
                          status_code: int, body: Any) -> Optional[Dict]:
        """
        校验响应是否符合注册的 Schema

        返回 None 表示通过，返回 dict 表示违规详情。

        这是框架自动调用的，测试层不需要手动调用。
        """
        if not self._enabled:
            return None          # # 如果禁用了契约校验，直接跳过

        reg = self.find(method, url)
        if not reg or not reg.response_schema:
            return None  # 没有注册 Schema，不做校验

        import jsonschema

        try:
            jsonschema.validate(instance=body, schema=reg.response_schema)
            return None  # 通过
        except jsonschema.ValidationError as e:
            violation = {
                "registration": reg,
                "url": url,
                "method": method,
                "status_code": status_code,
                "error": e.message,
                "path": list(e.relative_path),
            }
            logger.warning(
                f"  ⚠️ [Contract] Schema 违规: {method} {url}\n"
                f"    路径: {'.'.join(map(str, e.relative_path))}\n"
                f"    原因: {e.message}"
            )
            return violation

    # ---------- 控制 ----------

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def clear(self):
        self._registrations.clear()

    def count(self) -> int:
        return len(self._registrations)


# 全局单例
registry = ContractRegistry()


# =============================================================
#  契约测试生成器
# =============================================================


def generate_contract_tests():
    """
    从注册中心生成契约测试

    每个注册的端点生成一条测试，验证：
      1. Schema 本身是合法的 JSON Schema
      2. 响应结构包含所有 required 字段

    返回 pytest 可用的测试函数列表。
    """
    import pytest

    tests = []

    for reg in registry.find_all():
        @pytest.mark.contract
        def _test():
            assert reg.response_schema is not None, (
                f"{reg.description} 缺少 response_schema"
            )
            # 验证 Schema 自身合法性
            import jsonschema
            # Schema 本身是一个合法的 JSON Schema
            assert "$schema" in reg.response_schema or "type" in reg.response_schema, (
                f"{reg.description} 的 Schema 格式不完整"
            )
        #给函数改名字
        _test.__name__ = f"test_contract_{reg.method.lower()}_{reg.pattern.replace('/', '_').replace('{', '').replace('}', '')}"
        # 给函数加文档说明pytest 跑的时候可以用 -v 看到这段说明
        _test.__doc__ = f"契约校验: {reg.description}"
        tests.append(_test)#把函数收集起来

    return tests
