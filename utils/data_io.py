"""JSON 数据读写（GitHub 持久化 + Streamlit 缓存）

数据同时保存在本地文件和 GitHub 仓库中。
写入时：先写本地文件，再异步推送到 GitHub。
读取时：优先读本地缓存，本地不存在则从 GitHub 拉取。
应用重启时：本地文件丢失，自动从 GitHub 恢复。
"""
import json
import os
import base64
import requests
import streamlit as st
from config import DATA_DIR


# ── GitHub API 配置 ──
def _gh_config():
    """从 st.secrets 读取 GitHub 配置"""
    gh = st.secrets.get("github", {})
    return {
        "token": gh.get("token", ""),
        "repo": gh.get("repo", ""),       # 格式: owner/repo
        "branch": gh.get("branch", "main"),
        "data_path": gh.get("data_path", "data"),
    }


def _gh_headers():
    cfg = _gh_config()
    return {
        "Authorization": f"token {cfg['token']}",
        "Accept": "application/vnd.github.v3+json",
    }


def _gh_file_url(name: str) -> str:
    cfg = _gh_config()
    return f"https://api.github.com/repos/{cfg['repo']}/contents/{cfg['data_path']}/{name}"


def _gh_enabled() -> bool:
    cfg = _gh_config()
    return bool(cfg["token"] and cfg["repo"])


# ── 本地文件操作 ──
def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _file_path(name: str) -> str:
    _ensure_data_dir()
    return os.path.join(DATA_DIR, name)


def _read_local(name: str):
    """读取本地文件，不存在返回 None"""
    path = _file_path(name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _write_local(name: str, data):
    """写入本地文件"""
    path = _file_path(name)
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── GitHub 读写 ──
def _read_from_github(name: str):
    """从 GitHub 仓库读取 JSON 文件"""
    if not _gh_enabled():
        return None
    try:
        cfg = _gh_config()
        resp = requests.get(
            _gh_file_url(name),
            headers=_gh_headers(),
            params={"ref": cfg["branch"]},
            timeout=10,
        )
        if resp.status_code == 200:
            content = base64.b64decode(resp.json()["content"]).decode("utf-8")
            return json.loads(content)
        return None
    except Exception:
        return None


def _get_file_sha(name: str) -> str | None:
    """获取 GitHub 上文件的 SHA（更新文件时需要）"""
    if not _gh_enabled():
        return None
    try:
        cfg = _gh_config()
        resp = requests.get(
            _gh_file_url(name),
            headers=_gh_headers(),
            params={"ref": cfg["branch"]},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("sha")
        return None
    except Exception:
        return None


def _write_to_github(name: str, data):
    """将 JSON 数据写入 GitHub 仓库"""
    if not _gh_enabled():
        return
    try:
        content = json.dumps(data, ensure_ascii=False, indent=2)
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        cfg = _gh_config()

        body = {
            "message": f"data: update {name}",
            "content": encoded,
            "branch": cfg["branch"],
        }

        sha = _get_file_sha(name)
        if sha:
            body["sha"] = sha

        requests.put(
            _gh_file_url(name),
            headers=_gh_headers(),
            json=body,
            timeout=10,
        )
    except Exception:
        pass  # GitHub 写入失败不影响应用运行


# ── 对外接口（与原版完全一致） ──
@st.cache_data(ttl=3)
def read_json(name: str) -> dict | list:
    # 1. 先尝试本地
    data = _read_local(name)
    if data is not None:
        return data

    # 2. 本地没有，从 GitHub 恢复
    data = _read_from_github(name)
    if data is not None:
        _write_local(name, data)  # 缓存到本地
        return data

    # 3. 都没有，返回默认值
    default = {} if "users" in name or "pets" in name or "friends" in name or "shop" in name else []
    _write_local(name, default)
    return default


def write_json(name: str, data):
    _write_local(name, data)
    _write_to_github(name, data)
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
