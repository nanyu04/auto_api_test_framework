"""
测试数据 — 包导出
from data import DataFactory, factory, UserBuilder, OrderBuilder 别的地方导入直接这样写就行了
"""
from data.factory import DataFactory, factory
from data.builder import UserBuilder, OrderBuilder

__all__ = ["DataFactory", "factory", "UserBuilder", "OrderBuilder"]