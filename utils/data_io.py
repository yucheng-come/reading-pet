"""JSON 数据读写（带文件锁 + Streamlit 缓存）"""
import json
import os
import fcntl
import streamlit as st
from config import DATA_DIR


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _file_path(name: str) -> str:
    _ensure_data_dir()
    return os.path.join(DATA_DIR, name)


@st.cache_data(ttl=3)
def read_json(name: str) -> dict | list:
    path = _file_path(name)
    if not os.path.exists(path):
        default = {} if name.endswith(".json") else []
        _write_json_raw(name, default)
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


def _write_json_raw(name: str, data):
    """内部写入，不清缓存"""
    path = _file_path(name)
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(data, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def write_json(name: str, data):
    _write_json_raw(name, data)
    read_json.clear()


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
