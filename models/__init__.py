"""
【数据模型】 — 接口契约定义

这里不只是定义 Pydantic 模型，还自动向框架的契约注册中心注册。
注册之后，所有匹配的 HTTP 请求响应都会自动做 Schema 校验。
req = CreateUserRequest(name="张三", email="a@b.com", age=25)
payload = req.model_dump()      # → {"name": "张三", "email": "a@b.com", "age": 25, ...}
user_api.create(payload)
"""
from pathlib import Path

from pydantic import BaseModel, Field
from typing import Optional, Any


# =============================================================
#  请求模型
# =============================================================

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(...)
    age: int = Field(default=0, ge=0, le=150)
    phone: Optional[str] = Field(default=None)


class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    email: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=150)
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)


# =============================================================
#  响应模型
# =============================================================

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int = 0
    phone: Optional[str] = None
    created_at: Optional[str] = None


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


class PageData(BaseModel):
    total: int
    page: int
    page_size: int
    items: list


# =============================================================
#  JSON Schema 定义
# =============================================================
USER_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "name", "email"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string"},
        "age": {"type": "integer", "minimum": 0, "maximum": 150},
        "phone": {"type": ["string", "null"]},
        "created_at": {"type": ["string", "null"]},
    },
}

PAGE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["total", "page", "page_size", "items"],
    "properties": {
        "total": {"type": "integer", "minimum": 0},
        "page": {"type": "integer", "minimum": 1},
        "page_size": {"type": "integer", "minimum": 1},
        "items": {"type": "array"},
    },
}

API_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["code", "message"],
    "properties": {
        "code": {"type": "integer"},
        "message": {"type": "string"},
        "data": {},
    },
}


# =============================================================
#  【关键】向契约注册中心注册
#  注册后, 所有通过 HttpClient 的请求如果匹配端点,
#  会自动做响应体的 Schema 校验
# =============================================================

def register_user_contracts():
    """注册用户模块的所有 API 端点 Schema"""
    from framework.contract import registry

    # ========== 登录 ==========
    registry.register("POST", "/api/user/login",
                      response_schema=API_RESPONSE_SCHEMA,
                      description="用户登录")

    # ========== 学生注册 ==========
    registry.register("POST", "/api/student/user/register",
                      response_schema=API_RESPONSE_SCHEMA,
                      description="学生注册")

    # ========== 管理员 — 创建/编辑用户（同一个接口，id=null 创建，id 有值编辑） ==========
    registry.register("POST", "/api/admin/user/edit",
                      response_schema=API_RESPONSE_SCHEMA,
                      description="创建/编辑用户")

    # ========== 管理员 — 查询用户 ==========
    registry.register("POST", "/api/admin/user/select/{id}",
                      response_schema=API_RESPONSE_SCHEMA,
                      description="查询用户")

    # ========== 管理员 — 删除用户 ==========
    registry.register("DELETE", "/api/admin/user/delete/{id}",
                      response_schema=API_RESPONSE_SCHEMA,
                      description="删除用户")


# =============================================================
#  导出
# =============================================================

__all__ = [
    "CreateUserRequest", "UpdateUserRequest", "LoginRequest",
    "UserResponse", "ApiResponse", "PageData",
    "USER_SCHEMA", "PAGE_SCHEMA", "API_RESPONSE_SCHEMA",
    "register_user_contracts",
]
