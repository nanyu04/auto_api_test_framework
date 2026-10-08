"""
【HTTP 客户端】 — requests 封装

职责：
  - 统一管理 Session、鉴权、超时
  - 自动打印请求/响应日志
  - 请求失败重试（可配置）
  - 🔗 自动契约校验 —— 每次响应自动验证 Schema
"""
from typing import Any, Optional
import requests as req
from requests import Response, Session, Request
from config import settings
from common.logger import logger

class HttpClient:
    """
    底层的BASE_URL 封装在config里面
    HTTP 请求客户端
    用法：
        client = HttpClient()
        client.get()
        client.post()
        # 动态更新 token（登录后调用）
        client.set_token("new_token_here")

    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.BASE_URL).rstrip("/")
        # 加一个_不建议外部访问建议在内部访问
        self._session = Session()
        self._init_session()

    # ==================== 初始化 ====================

    def _init_session(self):
        """初始化 Session 默认值"""
        #① 第一批：业务默认头
        self._session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            #标明"是哪个客户端发的请求"（这里是你的测试框架）
            "User-Agent": f"ApiTestFramework/{settings.API_VERSION}",
        })
        # 注入全局鉴权② 第二批：鉴权头（来自配置）就是在请求头的位置加上鉴权
        self._session.headers.update(settings.auth_headers)

    # ==================== 公开请求方法 ====================

    def get(
        self, url: str, params: Optional[dict] = None,
        headers: Optional[dict] = None, **kwargs
    ) -> Response:
        return self.request("GET", url, params=params, headers=headers, **kwargs)

    def post(
        self, url: str, json: Any = None, data: Any = None,
        headers: Optional[dict] = None, **kwargs
    ) -> Response:
        return self.request("POST", url, json=json, data=data, headers=headers, **kwargs)

    def put(
        self, url: str, json: Any = None, data: Any = None,
        headers: Optional[dict] = None, **kwargs
    ) -> Response:
        return self.request("PUT", url, json=json, data=data, headers=headers, **kwargs)

    def patch(
        self, url: str, json: Any = None, data: Any = None,
        headers: Optional[dict] = None, **kwargs
    ) -> Response:
        return self.request("PATCH", url, json=json, data=data, headers=headers, **kwargs)

    def delete(
        self, url: str, headers: Optional[dict] = None, **kwargs
    ) -> Response:
        return self.request("DELETE", url, headers=headers, **kwargs)

    # ==================== 核心请求方法 ====================

    def request(self, method: str, url: str, **kwargs) -> Response:
        """
        统一请求入口

        在此处统一处理：
          - URL 拼接
          - 超时
          - 日志打印
          - 异常包装
        """
        full_url = self._build_url(url)
        #这个就是取值 取得到就用kwargs的值  提取不到就用默认值
        timeout = kwargs.pop("timeout", settings.REQUEST_TIMEOUT)
        extra_headers = kwargs.pop("headers", None)

        # 构造 PreparedRequest 造一个"请求意图"
        req_obj = Request(method, full_url, headers=extra_headers, **kwargs)
        #为什么要使用分三步发送请求呢？不能直接一步到位get post
        # 用 prepare_request 手动拆开 → 你手里有"发送前的完整请求"（prepped），想打印就打印，想改就改
        # 用 session.get/post 简写 → 一步到位直接返回 resp，中间那个"即将发出的请求"你根本没机会碰到
        prepped = self._session.prepare_request(req_obj)#② 把它"加工"成可发送的形态

        # 打印请求日志
        logger.print_request(method, full_url, dict(prepped.headers), prepped.body)

        # 发送请求
        try:
            # 真正发出去
            resp = self._session.send(prepped, timeout=timeout)
        except req.Timeout:
            logger.error(f"⏰ 请求超时 [{timeout}s]: {method} {full_url}")
            raise
        except req.ConnectionError as e:
            logger.error(f"🔌 连接被拒绝: {method} {full_url} — {e}")
            raise
        except req.RequestException as e:
            logger.error(f"❌ 请求异常: {method} {full_url} — {e}")
            raise

        # 🔗 自动契约校验（如果该端点已注册 Schema）
        self._validate_contract(method, full_url, resp)

        # 打印响应日志
        logger.print_response(
            resp.status_code, full_url,
            dict(resp.headers), self._safe_body(resp),
        )

        return resp

    # ==================== 辅助方法 ====================

    def _build_url(self, url: str) -> str:
        """拼接完整 URL"""
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return f"{self.base_url}/{url.lstrip('/')}"

    @staticmethod
    def _safe_body(response: Response) -> str:
        """安全获取响应体（防止日志过大）"""
        try:
            text = response.text
        except Exception:
            return "<body unreadable>"
        return text

    # ---------- 契约校验 ----------

    def _validate_contract(self, method: str, url: str, response: Response):
        """自动执行契约校验"""
        try:
            # 延迟导入避免循环引用
            from framework.contract import registry
            if registry.is_enabled:
                try:
                    #拿到响应，把响应体从 JSON 字符串解析成 Python 字典，存到 body 变量里。
                    body = response.json()
                except Exception:
                    body = None
                if body is not None:
                    registry.validate_response(method, url, response.status_code, body)
        except Exception:
            pass  # 契约校验失败不影响主流程

    # ==================== 公共接口 ====================

    def set_token(self, token: str):
        """动态更新 Bearer Token（登录后调用）"""
        self._session.headers["Authorization"] = f"Bearer {token}"
        logger.info("🔐 Token 已更新")

    def set_header(self, key: str, value: str):
        """动态设置请求头"""
        self._session.headers[key] = value

    def clear_auth(self):
        """清除鉴权头"""
        self._session.headers.pop("Authorization", None)
        self._session.headers.pop(settings.API_KEY_HEADER, None)

    @property
    def session(self) -> Session:
        """暴露原始 Session，用于高级定制"""
        return self._session

    def close(self):
        """关闭会话"""
        self._session.close()