"""
【数据工厂】 — 基于 Faker 的测试数据生成

每个方法生成业务含义明确的测试数据，支持 override 覆盖特定字段。
data.update(overrides) 就是把传进来的参数盖到默认数据上面。

"""
from typing import Any, Optional
from faker import Faker
#用中文词库来造假
_faker = Faker(locale="zh_CN")
#Faker(locale="en_US")	John Smith、Alice Brown

class DataFactory:
    """测试数据工厂"""

    # ========== 用户相关 ==========


    @staticmethod
    def create_user_payload(**overrides: Any) -> dict:
        """创建用户请求数据"""
        data = {
            "name": _faker.name(),
            "email": _faker.email(),
            "age": _faker.random_int(18, 60),
            "phone": _faker.phone_number(),
        }
        data.update(overrides)
        return data

    # ========== 订单相关 ==========

    @staticmethod
    def create_order_payload(**overrides: Any) -> dict:
        """创建订单请求数据"""
        data = {
            "order_no": f"ORD{_faker.unique.random_number(8)}",
            "amount": round(float(_faker.pyfloat(min_value=1, max_value=99999)), 2),
            "currency": _faker.random_element(["CNY", "USD", "EUR"]),
            "status": "pending",
        }
        data.update(overrides)
        return data

    # ========== 鉴权相关 ==========

    @staticmethod
    def login_payload(**overrides: Any) -> dict:
        """登录请求数据"""
        data = {
            "username": _faker.user_name(),
            "password": _faker.password(length=12),
        }
        data.update(overrides)
        return data

    # ========== 通用 ==========
    #max_nb_chars，意思是 "最多生成多少个字符"。
    @staticmethod
    def text(min_len: int = 5, max_len: int = 50) -> str:
        return _faker.text(max_nb_chars=max_len)[:max_len]

    @staticmethod
    def int_num(min_v: int = 1, max_v: int = 10000) -> int:
        return _faker.random_int(min_v, max_v)

    @staticmethod
    def phone() -> str:
        return _faker.phone_number()

    @staticmethod
    def email() -> str:
        return _faker.email()

    @staticmethod
    def url() -> str:
        return _faker.url()


# 全局工厂实例
factory = DataFactory()