"""
【工具 — 通用辅助函数】
"""
import json
import time
from typing import Any
from datetime import datetime


def current_timestamp() -> int:
    """当前时间戳（秒）"""
    return int(time.time())


def current_datetime(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """当前时间字符串"""
    return datetime.now().strftime(fmt)


def read_json_file(path: str) -> Any:
    """读取 JSON 文件"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def to_pretty_json(obj: Any) -> str:
    """对象转为格式化 JSON 字符串"""
    return json.dumps(obj, ensure_ascii=False, indent=2)


def merge_dict(base: dict, override: dict) -> dict:
    """合并两个字典（override 覆盖 base）"""
    result = base.copy()
    result.update(override)
    return result


def extract_values(data: list[dict], key: str) -> list:
    """从字典列表中提取指定 key 的值"""
    return [item[key] for item in data if key in item]


def mask_sensitive(text: str, keep: int = 4) -> str:
    """
    脱敏处理

    mask_sensitive("13812345678") → "138****5678"
    """
    if len(text) <= keep:
        return text
    return text[:keep] + "*" * (len(text) - keep * 2) + text[-keep:]