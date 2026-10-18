"""
【日志模块】 — 基于 loguru 的统一日志

特征：
  - 自动打印 请求/响应 详情，方便调试
  - 控制台彩色输出 + 文件持久化（按天轮转）
  - 支持 json 格式输出，便于日志采集系统
"""
import sys
import json
from pathlib import Path
from loguru import logger
from config import settings


class LogManager:
    """日志管理器"""
    def __init__(self):
        self._logger = logger
        self._setup()

    def _setup(self):
        """初始化日志配置"""
        self._logger.remove()  # 移除默认 handler

        log_dir = settings.ROOT_DIR / "logs"
        log_dir.mkdir(exist_ok=True)

        # ----- 控制台输出 -----
        if settings.LOG_FORMAT == "json":
            # 必须把 JSON 输出做成函数 sink：写成 format= 的话 loguru 会把渲染结果再当模板解析一次，导致 KeyError 丢日志
            # 目标位置由 _json_sink 内部写 stderr
            self._logger.add(
                self._json_sink,
                level=settings.LOG_LEVEL,
            )
        else:
            self._logger.add(
                sys.stderr,
                level=settings.LOG_LEVEL,
                format=(
                    "<green>{time:YY-MM-DD HH:mm:ss}</green> "
                    "| <level>{level:<5}</level> "
                    "| <cyan>{file}:{line}</cyan> "
                    "| <level>{message}</level>"
                ),
                colorize=True,
            )

        # ----- 文件输出（全量保留 30 天） -----
        self._logger.add(
            log_dir / "api_test_{time:YYYY-MM-DD}.log",
            level="DEBUG",
            rotation="00:00",
            retention="30 days",
            compression="gz",
            encoding="utf-8",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <5} | "
                "{file}:{function}:{line} | {message}"
            ),
        )

        # ----- 错误日志独立文件 -----
        self._logger.add(
            log_dir / "error_{time:YYYY-MM-DD}.log",
            level="ERROR",
            rotation="00:00",
            retention="60 days",
            compression="gz",
            encoding="utf-8",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <5} | "
                "{file}:{function}:{line} | {message}"
            ),
        )
    #---------------给机器使用的日志------------------
    @staticmethod
    def _json_sink(message):
        """JSON 格式日志 sink（供日志采集系统使用）

        作为 sink 函数交给 logger.add()：loguru 会把带 .record 的 message 传进来，
        我们在这里自己写 stderr。字段结构和以前完全一样，但转义交给 json.dumps
        （日志里经常带引号和换行，比如请求体，所以不能自己拼字符串模板）。
        """
        record = message.record
        sys.stderr.write(
            json.dumps(
                {
                    "time": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "level": record["level"].name,
                    "module": record["file"].name,
                    "line": record["line"],
                    "message": record["message"],
                },
                ensure_ascii=False,
            ) + "\n"
        )

    # ---------- 快捷方法，打印请求/响应详情 ----------

    def print_request(self, method: str, url: str, headers: dict, body):
        """打印请求详情"""
        body_preview = self._truncate(body, 2000)
        self._logger.debug(
            f"➡️  {method}  {url}\n"
            f"   Headers : {dict(headers)}\n"
            f"   Body    : {body_preview}"
        )

    def print_response(self, status: int, url: str, headers: dict, body):
        """打印响应详情"""
        body_preview = self._truncate(body, 3000)
        self._logger.debug(
            f"⬅️  {status}  {url}\n"
            f"   Headers : {dict(headers)}\n"
            f"   Body    : {body_preview}"
        )

    @staticmethod
    def _truncate(data, limit: int) -> str:
        text = str(data)
        return text[:limit] + "..." if len(text) > limit else text
    # 未显式定义的日志方法（info / warning / error 等）直接透传给 loguru
    def __getattr__(self, name):
        return getattr(self._logger, name)

# 全局日志实例
logger = LogManager()