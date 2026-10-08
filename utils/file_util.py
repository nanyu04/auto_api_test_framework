"""
【工具 — 文件操作】
"""
import csv
import json
from pathlib import Path
from typing import Any, List, Dict

import yaml


def read_csv(path: str) -> List[Dict[str, str]]:
    """读取 CSV → 字典列表"""
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: str, data: List[Dict[str, Any]], fieldnames: list = None):
    """写入 CSV"""
    if not fieldnames and data:
        fieldnames = list(data[0].keys())
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames or [])
        writer.writeheader()
        writer.writerows(data)


def read_json(path: str) -> Any:
    """读取 JSON"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, data: Any, pretty: bool = True):
    """写入 JSON"""
    with open(path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            json.dump(data, f, ensure_ascii=False)


def read_yaml(path: str) -> Any:
    """读取 YAML/YML 文件"""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: str, data: Any):
    """写入 YAML 文件"""
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, indent=2, sort_keys=False)


def ensure_dir(path: str) -> Path:
    """确保目录存在"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).resolve().parent.parent