"""
conftest — 框架级测试基础设施

在 pytest 进程启动时：
  1. 加载 models/ 中的 Schema 注册 → 契约中心自动生效
  2. 给每个测试一个唯一的 TestContext → 数据隔离
  3. 按模式启停 MockServer → mock/live 无感切换
"""
import pytest
from common import HttpClient, logger
from config import settings
from framework import (
    TestContext, MockServer, MockMode, registry,
)

# tests/fixtures/ 下的模块不会被自动加载，必须在这里显式注册
pytest_plugins = ["tests.fixtures.user_fixtures"]


# ==================== 初始化钩子（session 启动时执行一次） ====================

# pytest_configure: 收集用例前执行一次，用于加载契约注册
def pytest_configure(config):
    """pytest 配置阶段：加载 Schema 注册 + Allure 环境信息"""
    from models import register_user_contracts
    register_user_contracts()
    logger.info(f"📋 [框架] 契约注册完成: {registry.count()} 条端点")

    # Allure 报告环境信息
    allure_dir = getattr(config.option, 'allure_report_dir', None) or "reports/allure"
    if allure_dir:
        from pathlib import Path
        env_file = Path(allure_dir) / "environment.properties"
        env_file.parent.mkdir(parents=True, exist_ok=True)
        env_file.write_text(
            f"Environment={settings.ENV}\n"
            f"BaseURL={settings.BASE_URL}\n"
            f"Mode=hybrid\n"
        )


# ==================== 命令行参数 ====================

def pytest_addoption(parser):
    parser.addoption("--mode", action="store", default="hybrid",
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

# session 级共享客户端：用例间复用连接，退出时统一关闭
@pytest.fixture(scope="session")
def global_client() -> HttpClient:
    client = HttpClient()
    yield client
    client.close()

# 接口层必须复用这个会话：否则登录发生在 user_api 自己的会话上，
# 而清理走的是 global_client，请求不带登录态，自动清理会静默失败
@pytest.fixture(scope="session", autouse=True)
def bind_api_client(global_client):
    from apis import auth_api, user_api
    user_api.client = global_client
    auth_api.client = global_client
    yield

@pytest.fixture(scope="session")
def mock_server(test_mode) -> MockServer:
    ms = MockServer(settings.BASE_URL)
    if test_mode in (MockMode.MOCK, MockMode.HYBRID):
        ms.start(mode=test_mode)
    yield ms
    ms.stop()


@pytest.fixture
def mock_session(mock_server):
    """
    函数级 Mock，用完自动清理，不会污染其他用例。

    解决 session 级 mock_server 的问题：
      用例 A 注册了 POST /api/student/user/update
      → 用例 B（真实请求）的同 URL 被 mock 拦截，拿到假数据。

    用法：
        def test_mock_xxx(mock_session, logged_in_student):
            profile = MockProfile("test")
            profile.post("/some/url", MockResponse(200, body="ok"))
            mock_session.load(profile)
            ...  # mock 只在当前用例生效，结束自动清除
    """
    yield mock_server
    mock_server.reset()


# ==================== 测试级：隔离 + 生命周期 ====================


@pytest.fixture
def context(request, global_client) -> TestContext:
    """
    每个用例独享一个上下文。

      - context.identity    本次运行的唯一标识，用作数据标记
      - context.tag(data)   给 payload 的 name / username / email 等字段加唯一前缀
      - context.lifecycle   登记本次创建的数据，测试结束按依赖顺序自动清理
    """
    ctx = TestContext(request.node.name, global_client)
    yield ctx
    if not request.config.getoption("--no-cleanup"):
        ctx.cleanup()


@pytest.fixture
def api_client(global_client) -> HttpClient:
    """API 客户端"""
    return global_client
