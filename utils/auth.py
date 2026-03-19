"""认证系统：注册 / 登录 / 修改密码"""
import hashlib
from utils.data_io import read_json, update_dict
from config import ADMIN_ACCOUNT


def _hash_password(password: str, student_id: str) -> str:
    return hashlib.sha256((password + student_id).encode()).hexdigest()


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
        from utils.data_io import write_json
        write_json("users.json", users)


def register(student_id: str, name: str, college: str, major: str, password: str) -> tuple[bool, str]:
    if not all([student_id, name, college, major, password]):
        return False, "所有字段均为必填"
    if len(password) < 6:
        return False, "密码长度不能少于6位"
    users = read_json("users.json")
    if student_id in users:
        return False, "该学号已注册"
    users[student_id] = {
        "student_id": student_id,
        "name": name,
        "college": college,
        "major": major,
        "password": _hash_password(password, student_id),
        "is_admin": False,
    }
    from utils.data_io import write_json
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
