"""JSON 数据读写（带文件锁）"""
import json
import os
import fcntl
from config import DATA_DIR


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _file_path(name: str) -> str:
    _ensure_data_dir()
    return os.path.join(DATA_DIR, name)


def read_json(name: str) -> dict | list:
    path = _file_path(name)
    if not os.path.exists(path):
        default = {} if name.endswith(".json") else []
        write_json(name, default)
        return default
    with open(path, "r", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {} if name.endswith(".json") else []
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return data


def write_json(name: str, data):
    path = _file_path(name)
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(data, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def append_to_list(name: str, item):
    data = read_json(name)
    if not isinstance(data, list):
        data = []
    data.append(item)
    write_json(name, data)


def update_dict(name: str, key: str, value):
    data = read_json(name)
    if not isinstance(data, dict):
        data = {}
    data[key] = value
    write_json(name, data)
