"""
====================================================
  API 自动化测试框架 — 全局配置中心
  基于 pydantic-settings，支持多环境 + 环境变量覆盖
  Basesetting将类属性转变为实例属性直接调
====================================================
"""
from pathlib import Path
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class GlobalConfig(BaseSettings):
    """
    全局配置
    读取优先级：
      实例化传参 > 环境变量 > .env 文件 > 默认值

    用法：
      from config import settings
      settings.BASE_URL
    """

    # -------------------- 项目路径 --------------------
    # 拿到项目的根目录  Path(__file__) 项目的绝对路径 .resolve()切换为绝对路径
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent

    # -------------------- 环境选择 --------------------
    ENV: Literal["dev", "test", "staging", "prod"] = "dev"

    # -------------------- 被测服务 --------------------
    BASE_URL: str = "http://127.0.0.1:8000"
    API_VERSION: str = "v1"

    # -------------------- 请求默认值 --------------------
    REQUEST_TIMEOUT: int = 15  # 超时（秒）
    MAX_RETRIES: int = 3  # 最大重试次数
    RETRY_DELAY: float = 1.0  # 重试间隔（秒）
    RETRY_MULTIPLIER: float = 2.0  # 退避倍数

    # -------------------- 鉴权配置 --------------------
    AUTH_TYPE: Literal["bearer", "basic", "apikey"] = "bearer"
    ACCESS_TOKEN: Optional[str] = None
    API_KEY: Optional[str] = None
    API_KEY_HEADER: str = "X-API-Key"
    USERNAME: Optional[str] = None
    PASSWORD: Optional[str] = None

    # -------------------- 日志配置 --------------------
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "standard"  # standard  人读日志文本 | json 机器读取 输出形式

    # -------------------- 报告配置 --------------------
    ALLURE_DIR: Path = ROOT_DIR / "reports" / "allure"
    REPORT_TITLE: str = "API 自动化测试报告"

    # -------------------- 数据库（可选） --------------------
    DB_HOST: Optional[str] = None
    DB_PORT: int = 3306
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,#区分大小写？
        extra="ignore",
    )

    # **一个方法（函数）伪装成实例属性**。 这个是用来自动使用请求头
    @property
    def auth_headers(self) -> dict:
        """返回鉴权请求头"""
        headers = {}
        if self.AUTH_TYPE == "bearer" and self.ACCESS_TOKEN:
            headers["Authorization"] = f"Bearer {self.ACCESS_TOKEN}"
        elif self.AUTH_TYPE == "apikey" and self.API_KEY:
            headers[self.API_KEY_HEADER] = self.API_KEY
        return headers


# 全局唯一配置实例
settings = GlobalConfig()
