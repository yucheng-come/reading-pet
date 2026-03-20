"""认证系统：注册 / 登录 / 修改密码 / 批量导入"""
import hashlib
from utils.data_io import read_json, update_dict, write_json
from config import ADMIN_ACCOUNT


def _hash_password(password: str, student_id: str) -> str:
    return hashlib.sha256((password + student_id).encode()).hexdigest()


def id_card_to_password(id_card: str) -> str:
    """身份证后八位作为密码，X 用 0 代替"""
    last8 = id_card[-8:].upper().replace("X", "0")
    return last8


def _init_admin():
    users = read_json("users.json")
    aid = ADMIN_ACCOUNT["student_id"]
    if aid not in users:
        users[aid] = {
            "student_id": aid,
            "name": ADMIN_ACCOUNT["name"],
            "college": ADMIN_ACCOUNT["college"],
            "major": ADMIN_ACCOUNT["major"],
            "password": _hash_password(ADMIN_ACCOUNT["password_raw"], aid),
            "is_admin": True,
        }
        write_json("users.json", users)


def register(student_id: str, name: str, college: str, major: str, id_card: str) -> tuple[bool, str]:
    if not all([student_id, name, college, major, id_card]):
        return False, "所有字段均为必填"
    if len(id_card) < 8:
        return False, "身份证号码长度不正确"
    users = read_json("users.json")
    if student_id in users:
        return False, "该学号已注册"
    password = id_card_to_password(id_card)
    users[student_id] = {
        "student_id": student_id,
        "name": name,
        "college": college,
        "major": major,
        "id_card_last8": password,
        "password": _hash_password(password, student_id),
        "is_admin": False,
    }
    write_json("users.json", users)
    return True, "注册成功！"


def login(student_id: str, password: str) -> tuple[bool, str]:
    _init_admin()
    users = read_json("users.json")
    if student_id not in users:
        return False, "学号不存在"
    user = users[student_id]
    if user["password"] != _hash_password(password, student_id):
        return False, "密码错误"
    return True, "登录成功"


def change_password(student_id: str, old_password: str, new_password: str) -> tuple[bool, str]:
    users = read_json("users.json")
    user = users.get(student_id)
    if not user:
        return False, "用户不存在"
    if user["password"] != _hash_password(old_password, student_id):
        return False, "旧密码错误"
    if len(new_password) < 6:
        return False, "新密码长度不能少于6位"
    user["password"] = _hash_password(new_password, student_id)
    update_dict("users.json", student_id, user)
    return True, "密码修改成功"


def get_user(student_id: str) -> dict | None:
    users = read_json("users.json")
    return users.get(student_id)


def is_admin(student_id: str) -> bool:
    user = get_user(student_id)
    return user.get("is_admin", False) if user else False


def batch_import_users(records: list[dict]) -> tuple[int, int, list[str]]:
    """批量导入用户，records 每项需包含 student_id, name, college, major, id_card。
    返回 (成功数, 跳过数, 错误信息列表)"""
    users = read_json("users.json")
    success = 0
    skipped = 0
    errors = []
    for i, r in enumerate(records):
        sid = str(r.get("student_id", "")).strip()
        name = str(r.get("name", "")).strip()
        college = str(r.get("college", "")).strip()
        major = str(r.get("major", "")).strip()
        id_card = str(r.get("id_card", "")).strip()
        if not all([sid, name, college, major, id_card]):
            errors.append(f"第{i+1}行：信息不完整，已跳过")
            skipped += 1
            continue
        if sid in users:
            skipped += 1
            continue
        password = id_card_to_password(id_card)
        users[sid] = {
            "student_id": sid,
            "name": name,
            "college": college,
            "major": major,
            "id_card_last8": password,
            "password": _hash_password(password, sid),
            "is_admin": False,
        }
        success += 1
    write_json("users.json", users)
    return success, skipped, errors


def reset_password_by_idcard(student_id: str, id_card: str) -> tuple[bool, str]:
    """用身份证后八位重置密码"""
    users = read_json("users.json")
    user = users.get(student_id)
    if not user:
        return False, "用户不存在"
    password = id_card_to_password(id_card)
    user["password"] = _hash_password(password, student_id)
    user["id_card_last8"] = password
    update_dict("users.json", student_id, user)
    return True, f"密码已重置为身份证后八位"
