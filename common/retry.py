"""
【重试机制】 — 基于 tenacity 的重试装饰器

用于处理网络抖动、服务暂时不可用等场景。
"""
from typing import Callable, Type, Optional, Tuple
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError,
)
from common.logger import logger


def retry_on_failure(
    max_attempts: Optional[int] = None,
    min_delay: float = 0.5,
    max_delay: float = 10.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    reraise: bool = True,
):
    """
    自动重试装饰器

    用法：
        @retry_on_failure()
        def unstable_request():
            ...

        @retry_on_failure(max_attempts=5, exceptions=(TimeoutError,))
        def slow_request():
            ...

    参数：
        max_attempts:  最大尝试次数（默认 settings.MAX_RETRIES）
        min_delay:     初始等待秒数
        max_delay:     最大等待秒数
        exceptions:    哪些异常触发重试
        reraise:       重试耗尽后是否抛异常
    """
    from config import settings as _cfg

    return retry(
        stop=stop_after_attempt(max_attempts or _cfg.MAX_RETRIES),
        wait=wait_exponential(
            multiplier=_cfg.RETRY_MULTIPLIER,
            min=min_delay,
            max=max_delay,
        ),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=reraise,
    )


def safe_call(func: Callable, *args, **kwargs):
    """
    安全调用函数，失败后返回 None 而非抛异常

    用法：
        result = safe_call(unstable_func, arg1, arg2)
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"安全调用失败: {e}")
        return None