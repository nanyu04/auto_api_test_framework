"""
framework/mock — Mock 子系统

企业级 Mock 的三个能力：
  1. Profile 定义：声明式定义整个 API 的行为
  2. 自动匹配：按 URL + method + body pattern 自动路由
  3. 模式切换：同一套测试在 mock/live 下无感切换
  MockMode          → 决定"开关"（是否启用 Mock）
                     ↓
MockResponse      → 定义"返回什么"（状态码、响应体、响应头）
                     ↓
MockRoute         → 定义"拦截什么"（method + URL pattern）→ 绑定 MockResponse
                     ↓
MockProfile       → 把一组 MockRoute 打包，给个名字方便管理
                     ↓
MockServer        → 真正的"执行者"
                      1. respx.mock()  → 建拦截器
                      2. start()       → 启动拦截
                      3. load + _apply_profile  → 把 Profile 里的路由注册进 respx
"""
import os
import json
from enum import Enum
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass, field
from common.logger import logger
from config import settings


# =============================================================
#  Mock 模式
# =============================================================


class MockMode(Enum):
    LIVE = "live"    # 请求真实服务
    MOCK = "mock"    # 全部拦截
    HYBRID = "hybrid"  # 注册了的 mock，没注册的透传


def current_mode() -> MockMode:
    """获取当前模式"""
    raw = os.getenv("TEST_MODE", "live").lower()
    return MockMode(raw)


# =============================================================
#  Mock 定义结构
# =============================================================

#装着假相应的数据容器
@dataclass
class MockResponse:
    status: int = 200
    body: Any = None
    #相当于每次创建了这个类的对象都会重新生成一个headers生成一个独立的新字典
    headers: Dict[str, str] = field(default_factory=lambda: {"content-type": "application/json"})


@dataclass
class MockRoute:
    """一条 mock 路由"""
    method: str
    pattern: str           # URL 模式，支持 {id} 占位
    response: MockResponse
    dynamic: bool = False  # 是否根据请求动态生成响应


class MockProfile:
    """
    Mock Profile — 声明式 API 行为定义

    用法：
        profile = MockProfile("用户模块")
        profile.register("GET", "/api/v1/users/{id}",
                         MockResponse(200, {"code": 0, "data": {"id": 1, "name": "MockUser"}}))
        profile.register("POST", "/api/v1/users",
                         MockResponse(201, {"code": 0, "data": {"id": 999}}))
    """

    def __init__(self, name: str = "default"):
        self.name = name
        self._routes: List[MockRoute] = []

    def register(self, method: str, pattern: str,
                 response: MockResponse | dict, dynamic: bool = False):
        """注册一条 mock 路由"""
        #isinstance 检查是否是这两个类型
        if isinstance(response, dict):
            response = MockResponse(**response)
        self._routes.append(MockRoute(method.upper(), pattern, response, dynamic))
        logger.debug(f"  🎭 [Mock] {self.name}: {method.upper()} {pattern} → {response.status}")
        return self

    def get(self, pattern: str, response: MockResponse | dict, **kw):
        return self.register("GET", pattern, response, **kw)

    def post(self, pattern: str, response: MockResponse | dict, **kw):
        return self.register("POST", pattern, response, **kw)

    def put(self, pattern: str, response: MockResponse | dict, **kw):
        return self.register("PUT", pattern, response, **kw)

    def delete(self, pattern: str, response: MockResponse | dict, **kw):
        return self.register("DELETE", pattern, response, **kw)

    def get_routes(self) -> List[MockRoute]:
        return self._routes

    def merge(self, other: "MockProfile") -> "MockProfile":
        """合并另一个 profile"""
        self._routes.extend(other._routes)
        return self


# =============================================================
#  Mock Server
# =============================================================


class MockServer:
    """
    Mock Server — 基于 respx 的请求拦截

    职责：
      - 根据 MockMode 决定是否启用
      - 加载 MockProfile 注册路由
      - 动态响应生成（如需）
    """

    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")
        self._profiles: List[MockProfile] = []#存多个profile
        self._respx_mock = None#respx实例
        self._active = False

    def load(self, profile: MockProfile) -> "MockServer":
        """加载一个 Mock Profile"""
        self._profiles.append(profile)
        if self._active:
            self._apply_profile(profile)
        return self
    #初始化respx 加载路由
    def start(self):
        """启动 Mock（启用 respx 拦截）"""
        if self._active:
            return
        import respx
        #创建拦截器
        self._respx_mock = respx.mock(
            assert_all_called=False,
            using="httpx",
        )
        self._respx_mock.start()#调用respx 里面的start 启动服务
        self._active = True
        # 加载所有 profile 就是告诉他怎么拦截 加载路由
        for profile in self._profiles:
            self._apply_profile(profile)
        logger.info(f"  🎭 [MockServer] 已启动 (BASE: {self._base_url})")

    def stop(self):
        if self._active and self._respx_mock:
            self._respx_mock.stop()
            self._active = False
            logger.info("  🎭 [MockServer] 已停止")

    def _apply_profile(self, profile: MockProfile):
        """将 profile 的路由注册到 respx"""
        if not self._respx_mock:
            return
        for route in profile.get_routes():
            full_url = f"{self._base_url}/{route.pattern.lstrip('/')}"
            # 前半段 → 定义拦截规则："我要拦截发往 http://... 的 GET/POST 请求"
            # .respond() → 定义返回内容："拦截到以后，返回状态码 200、这段 JSON 和这些 headers"
            getattr(self._respx_mock, route.method.lower())(full_url).respond(
                status_code=route.response.status,
                json=route.response.body,
                headers=route.response.headers,
            )

    @property
    def is_active(self) -> bool:
        return self._active


