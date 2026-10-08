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
        # exist_ok=true 存在以后也不报错，不加的话 就是存在会报错
        log_dir.mkdir(exist_ok=True)

        # ----- 控制台输出 -----
        if settings.LOG_FORMAT == "json":
            self._logger.add(
                sys.stderr,# 需要输出到的位置  这个 sys.stderr 默认输出到控制台
                level=settings.LOG_LEVEL,
                format=self._json_format,#为什么要另外一个函数呢，就是因为这是给机器看的，不能用彩色标注那些
            )
        else:
            self._logger.add(
                sys.stderr,
                level=settings.LOG_LEVEL,
                format=(
                    "<green>{time:YY-MM-DD HH:mm:ss}</green> "
                    "| <level>{level:<5}</level> "#触发的级别
                    "| <cyan>{file}:{line}</cyan> "#触发这条日志的文件名
                    "| <level>{message}</level>"
                    #24-05-20 15:30:00 | INFO  | main.py:42 | 程序启动message   输出结果会是这样子的
                ),
                colorize=True,
            )

        # ----- 文件输出（全量保留 30 天） -----
        self._logger.add(
            log_dir / "api_test_{time:YYYY-MM-DD}.log",#输出目标文件的文件名
            level="DEBUG",#错误等级
            rotation="00:00",#每天午夜 0 点，loguru 会自动把当前日志文件关闭，并创建一个新的日志文件。
            retention="30 days",#保留时间 30 天
            compression="gz",# 过了午夜以后他就会自动压缩，压缩后的文件依然可以被查看
            encoding="utf-8", #编码格式
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <5} | "
                "{file}:{function}:{line} | {message}"#说明了是从哪个文件 哪个函数 哪一行出来的
            ),
        )

        # ----- 错误日志独立文件 -----
        self._logger.add(
            log_dir / "error_{time:YYYY-MM-DD}.log",#输出目标文件的文件名
            level="ERROR",  #错误等级
            rotation="00:00",#每天午夜 0 点，loguru 会自动把当前日志文件关闭，并创建一个新的日志文件。
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
    def _json_format(record):
        """JSON 格式日志（供日志采集系统使用）"""
        #这些record 写下日志以后都会立马自动生成的 就比如说logging.info() 就会马上生成对应的下面那些内容
        return json.dumps(
            {
                "time": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f"),
                "level": record["level"].name,
                "module": record["file"].name,
                "line": record["line"],
                "message": record["message"],
            },
            #确保中文能够正常显示
            ensure_ascii=False,
        ) + "\n"

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
    #写了这个方法的话，创建了LogManager对象 使用里面的方法 如果没有对应的方法 他就会调用self._logger=logger
    #然后 name 就是你调用的方法   其实就相当于直接调用了底层的 logger.方法名去替代
    def __getattr__(self, name):
        return getattr(self._logger, name)

# 全局日志实例
logger = LogManager()