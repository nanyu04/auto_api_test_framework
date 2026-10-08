"""
【数据构造器】 — 链式构造复杂测试数据

适用于参数组合较多的场景，比普通 dict 更易读。
"""
from dataclasses import dataclass, asdict
from typing import Optional


class UserBuilder:
    """用户测试数据构造器（链式调用）"""

    def __init__(self):
        self._name = "default_user"
        self._email = "default@example.com"
        self._age = 18
        self._phone = None

    def name(self, value: str) -> "UserBuilder":
        self._name = value
        return self

    def email(self, value: str) -> "UserBuilder":
        self._email = value
        return self

    def age(self, value: int) -> "UserBuilder":
        self._age = value
        return self

    def phone(self, value: str) -> "UserBuilder":
        self._phone = value
        return self

    def build(self) -> dict:
        d = {"name": self._name, "email": self._email, "age": self._age}
        if self._phone:
            d["phone"] = self._phone
        return d


class OrderBuilder:
    """订单测试数据构造器"""

    def __init__(self):
        self._data = {
            "order_no": "",
            "amount": 0.0,
            "currency": "CNY",
            "status": "pending",
        }

    def order_no(self, value: str) -> "OrderBuilder":
        self._data["order_no"] = value
        return self

    def amount(self, value: float) -> "OrderBuilder":
        self._data["amount"] = value
        return self

    def currency(self, value: str) -> "OrderBuilder":
        self._data["currency"] = value
        return self

    def status(self, value: str) -> "OrderBuilder":
        self._data["status"] = value
        return self

    def build(self) -> dict:
        return {**self._data}