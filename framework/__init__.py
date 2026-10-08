"""
framework — 框架核心

这里把三个子系统（隔离 / Mock / 契约）组装在一起，
对外提供 TestContext 和 MockServer，供 conftest 使用。
"""
from .isolation import TestContext, TestIdentity
from .mock import MockServer, MockProfile, MockMode, current_mode, default_user_profile
from .contract import registry, ContractRegistry

__all__ = [
    "TestContext", "TestIdentity",
    "MockServer", "MockProfile", "MockMode", "current_mode", "default_user_profile",
    "registry", "ContractRegistry",
]