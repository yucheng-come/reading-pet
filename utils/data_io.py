"""数据读写（MongoDB Atlas 持久化 + Streamlit 缓存）"""
import streamlit as st
from pymongo import MongoClient


@st.cache_resource
def _get_db():
    """单例 MongoDB 连接"""
    uri = st.secrets["mongo"]["uri"]
    db_name = st.secrets["mongo"]["db_name"]
    client = MongoClient(uri)
    return client[db_name]


def _col_name(name: str) -> str:
    """JSON 文件名 → 集合名，如 users.json → users"""
    return name.replace(".json", "")


# ── 内部默认值 ──
# dict 类型的集合（以 key-value 形式存储）
_DICT_COLLECTIONS = {"users", "pets", "friends", "shop"}


def _is_dict_type(name: str) -> bool:
    return _col_name(name) in _DICT_COLLECTIONS


@st.cache_data(ttl=3)
def read_json(name: str) -> dict | list:
    """读取数据，返回 dict 或 list，与原文件接口完全一致"""
    db = _get_db()
    col = db[_col_name(name)]

    if _is_dict_type(name):
        # dict 类型：每个文档的 _key 是字典键
        result = {}
        for doc in col.find():
            key = doc.pop("_key")
            doc.pop("_id", None)
            result[key] = doc
        return result
    else:
        # list 类型：每个文档是列表中的一项
        result = []
        for doc in col.find(sort=[("_order", 1)]):
            doc.pop("_id", None)
            doc.pop("_order", None)
            result.append(doc)
        return result


def write_json(name: str, data):
    """写入数据（全量覆盖），清除缓存"""
    db = _get_db()
    col = db[_col_name(name)]

    if _is_dict_type(name) and isinstance(data, dict):
        col.delete_many({})
        if data:
            docs = []
            for key, value in data.items():
                doc = {"_key": key}
                if isinstance(value, dict):
                    doc.update(value)
                else:
                    doc["_value"] = value
                docs.append(doc)
            col.insert_many(docs)
    elif isinstance(data, list):
        col.delete_many({})
        if data:
            docs = []
            for i, item in enumerate(data):
                doc = {"_order": i}
                if isinstance(item, dict):
                    doc.update(item)
                else:
                    doc["_value"] = item
                docs.append(doc)
            col.insert_many(docs)

    read_json.clear()


def append_to_list(name: str, item):
    """向列表类集合追加一项"""
    db = _get_db()
    col = db[_col_name(name)]

    # 获取当前最大 _order
    last = col.find_one(sort=[("_order", -1)])
    next_order = (last["_order"] + 1) if last and "_order" in last else 0

    doc = {"_order": next_order}
    if isinstance(item, dict):
        doc.update(item)
    else:
        doc["_value"] = item
    col.insert_one(doc)

    read_json.clear()


def update_dict(name: str, key: str, value):
    """更新 dict 类集合的某个 key"""
    db = _get_db()
    col = db[_col_name(name)]

    doc = {"_key": key}
    if isinstance(value, dict):
        doc.update(value)
    else:
        doc["_value"] = value

    col.replace_one({"_key": key}, doc, upsert=True)

    read_json.clear()
