"""
conftest — 框架级测试基础设施

在 pytest 进程启动时：
  1. 加载 models/ 中的 Schema 注册 → 契约中心自动生效
  2. 给每个测试一个唯一的 TestContext → 数据隔离
  3. 按模式启停 MockServer → mock/live 无感切换
  参数名对 fixture 名 → 自动注入值 ✅  所有 fixture
    都这样
  - autouse=True → 不用写参数也自动调 ✅
  - 普通 fixture → 你得在参数里写名字，pytest
    才知道调谁 ✅
  - conftest.py 只是"共享位置"，不是"自动执行" ✅
"""
import pytest
from common import HttpClient, logger
from config import settings
from framework import (
    TestContext, MockServer, MockMode, registry,
)


# ==================== 初始化钩子（session 启动时执行一次） ====================

#  pytest_configure  pytest 启动后、收集用例之前
def pytest_configure(config):
    """pytest 配置阶段：加载 Schema 注册"""
    from models import register_user_contracts
    register_user_contracts()
    logger.info(f"📋 [框架] 契约注册完成: {registry.count()} 条端点")


# ==================== 命令行参数 ====================

#解析命令行参数时
def pytest_addoption(parser):
    parser.addoption("--mode", action="store", default="live",
                     choices=["live", "mock", "hybrid"],
                     help="测试模式: live=真实服务, mock=全部Mock, hybrid=混合")
    parser.addoption("--no-cleanup", action="store_true", default=False,
                     help="保留测试数据（调试用）")


# ==================== Session 级 ====================


@pytest.fixture(scope="session")
def test_mode(request) -> MockMode:
    return MockMode(request.config.getoption("--mode"))


@pytest.fixture(scope="session", autouse=True)
def session_banner(test_mode):
    """打印环境信息"""
    logger.info("=" * 60)
    logger.info(f"🚀 环境: {settings.ENV}  |  🎯 地址: {settings.BASE_URL}")
    logger.info(f"🎭 模式: {test_mode.value}  |  📋 Schema: {registry.count()} 条")
    logger.info("=" * 60)
    yield
    logger.info("🏁 全部测试执行完毕")


@pytest.fixture(scope="session")
def global_client() -> HttpClient:
    client = HttpClient()
    yield client
    client.close()

#mock服务
@pytest.fixture(scope="session")
def mock_server(test_mode) -> MockServer:
    ms = MockServer(settings.BASE_URL)
    if test_mode in (MockMode.MOCK, MockMode.HYBRID):
        ms.start()
    yield ms
    ms.stop()


# ==================== 测试级：隔离 + 生命周期 ====================


@pytest.fixture
def context(request, global_client) -> TestContext:
    """
    【核心 Fixture】每个测试独立的上下文

    自动提供：
      ✅ context.identity  — 唯一身份（数据标记用）
      ✅ context.tag()     — 给数据打标
      ✅ context.lifecycle — 数据生命周期管理
      ✅ 测试结束自动清理（无论成功/失败）
      request.node.name 这个是他们自动填写的 是fixture的原因
      就相当于只要有人的参数填写了context 那么这request.node.name就自动导入了
    """
    ctx = TestContext(request.node.name, global_client)
    yield ctx
    if not request.config.getoption("--no-cleanup"):
        ctx.cleanup()


@pytest.fixture
def api_client(global_client) -> HttpClient:
    """API 客户端"""
    return global_client