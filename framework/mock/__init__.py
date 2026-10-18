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
                      1. 用 requests_mock.Mocker 建拦截器
                      2. start() 启动拦截
                      3. load(profile) 把 Profile 中的路由注册到拦截器
"""
import os
import json
import re
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
    MOCK = "mock"    # 全部拦截 没注册的直接报异常
    HYBRID = "hybrid"  # 注册了的 mock，没注册的透传


def current_mode() -> MockMode:
    """获取当前模式"""
    raw = os.getenv("TEST_MODE", "live").lower()
    return MockMode(raw)


# =============================================================
#  Mock 定义结构
# =============================================================

@dataclass
class MockResponse:
    status: int = 200
    body: Any = None
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
    Mock Server — 请求拦截

    职责：
      - 根据 MockMode 决定是否启用
      - 加载 MockProfile 注册路由
      - 动态响应生成（如需）

    底层用 requests_mock 拦截 requests 请求，与 HttpClient 使用的库一致。
    """

    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")
        self._profiles: List[MockProfile] = []
        self._mock_adapter = None          # requests_mock.Mocker 实例
        self._active = False

    def load(self, profile: MockProfile) -> "MockServer":
        """加载一个 Mock Profile"""
        self._profiles.append(profile)
        if self._active:
            self._apply_profile(profile)
        return self
    def start(self, mode: MockMode = MockMode.MOCK):
        """启动 Mock（启用 requests_mock 拦截）

        mode 决定未命中时的行为：
          MOCK   → 没注册的路由直接报 NoMockAddress（宁可炸，不悄悄放行）
          HYBRID → 没注册的路由透传给真实服务（real_http=True）
        """
        if self._active:
            return

        # ── 用 requests_mock 拦截 requests（HttpClient 走的正是 requests）──
        import requests_mock
        self._mock_adapter = requests_mock.Mocker(
            real_http=(mode == MockMode.HYBRID),  # HYBRID 允许未命中时走真实网络
        )
        self._mock_adapter.start()
        self._active = True
        # 加载 start() 之前已经 load 进来的 profile
        for profile in self._profiles:
            self._apply_profile(profile)
        logger.info(f"  🎭 [MockServer] 已启动 (BASE: {self._base_url})")

    def stop(self):
        # ── 停止拦截 ──
        if self._active and self._mock_adapter:
            self._mock_adapter.stop()
            self._active = False
            logger.info("  🎭 [MockServer] 已停止")

    def _apply_profile(self, profile: MockProfile):
        """将 profile 的路由注册到拦截器"""

        # ── 把路由注册到拦截器 ──
        if not self._mock_adapter:
            return
        for route in profile.get_routes():
            full_url = f"{self._base_url}/{route.pattern.lstrip('/')}"
            url = full_url
            # 把 {id} / {name} 这种占位符换成正则通配，
            # 否则 /api/v1/users/{id} 拦不到 /api/v1/users/123
            if "{" in full_url:
                url = re.compile(re.sub(r"\{[^}]+\}", r"[^/]+", full_url) + "$")
            getattr(self._mock_adapter, route.method.lower())(
                url,
                json=route.response.body,
                status_code=route.response.status,
                headers=route.response.headers,
            )

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def request_history(self):
        """返回所有被 mock 拦截的请求记录，用于验证请求参数是否正确发出"""
        if self._mock_adapter:
            return self._mock_adapter.request_history
        return []

    @property
    def last_request(self):
        """最后一次被 mock 拦截的请求，方便快速校验"""
        history = self.request_history
        #取最后一条
        return history[-1] if history else None

    def reset(self):
        """
        清除所有已注册的 mock 路由（函数级隔离）

        解决 session 级 MockServer 跨用例污染：
          用例 A 注册了 POST /api/student/user/update → 用例 B 的同 URL 真实请求被拦截。
        在函数级 fixture 中每次用完 reset，清理干净。
        """
        self._profiles.clear()
        if self._mock_adapter:
            self._mock_adapter.reset_mock()
            logger.debug("  🎭 [MockServer] 已清除所有 mock 路由")


