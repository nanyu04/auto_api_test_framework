"""
【重试工具】— 基于 tenacity 的测试重试装饰器

用于处理偶尔因网络抖动、服务延迟导致的用例失败。

用法一：装饰器 — 套在测试函数上
─────────────────────────────
    from common.retry import retry_on_failure

    @retry_on_failure(max_attempts=3, wait_seconds=2)
    def test_something(a_new_admin):
        ...

用法二：safe_call — 重试单个操作
─────────────────────────────
    from common.retry import safe_call

    resp = safe_call(user_api.create_user, url, payload, max_attempts=3)

参数：
    max_attempts: 最多执行次数（含第一次），默认 3
    wait_seconds: 两次重试之间的等待秒数，默认 2
"""
from tenacity import retry, stop_after_attempt, wait_fixed


def retry_on_failure(max_attempts: int = 3, wait_seconds: int = 2):
    """
    测试失败自动重试（装饰器版本）

    只对 AssertionError 生效，断言失败才重试。
    """
    return retry(
        reraise=True,#把最后一次的 AssertionError 原样抛出
        retry=stop_after_attempt(max_attempts),
        wait=wait_fixed(wait_seconds),
    )


def safe_call(func, *args, max_attempts: int = 3, wait_seconds: int = 2, **kwargs):
    """
    重试单个操作（函数调用版本）

    适用于只需要重试某一步 API 调用而非整个测试的场景。

    用法：
        resp = safe_call(user_api.create_user, url, payload, max_attempts=5)
    """
    @retry(reraise=True, retry=stop_after_attempt(max_attempts), wait=wait_fixed(wait_seconds))
    def _call():
        return func(*args, **kwargs)
    return _call()