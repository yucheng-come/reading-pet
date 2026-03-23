"""积分管理引擎"""
import uuid
from utils.data_io import read_json, write_json, append_to_list
from utils.time_utils import today_str, now_str
from config import POINTS_RULES


def get_balance(student_id: str) -> int:
    logs = read_json("points_log.json")
    return sum(l["amount"] for l in logs if l["student_id"] == student_id)


def _today_earned(student_id: str, action: str) -> int:
    logs = read_json("points_log.json")
    today = today_str()
    return sum(
        l["amount"] for l in logs
        if l["student_id"] == student_id and l["action"] == action
        and l["time"][:10] == today and l["amount"] > 0
    )


def earn_points(student_id: str, action: str, note: str = "", custom_points: int = 0) -> tuple[bool, str, int]:
    rule = POINTS_RULES.get(action)
    if not rule:
        return False, "未知行为类型", 0
    pts = custom_points if custom_points > 0 else rule["points"]
    daily_max = rule["daily_max"]
    if daily_max is not None:
        already = _today_earned(student_id, action)
        if already >= daily_max:
            return False, f"今日「{rule['label']}」积分已达上限 ({daily_max}分)", 0
        if already + pts > daily_max:
            pts = daily_max - already
    log_entry = {
        "id": str(uuid.uuid4())[:8],
        "student_id": student_id,
        "action": action,
        "amount": pts,
        "note": note or rule["label"],
        "time": now_str(),
    }
    append_to_list("points_log.json", log_entry)
    return True, f"+{pts} 积分（{rule['label']}）", pts


def spend_points(student_id: str, amount: int, note: str = "") -> tuple[bool, str]:
    balance = get_balance(student_id)
    if balance < amount:
        return False, f"积分不足（当前 {balance}，需要 {amount}）"
    log_entry = {
        "id": str(uuid.uuid4())[:8],
        "student_id": student_id,
        "action": "spend",
        "amount": -amount,
        "note": note,
        "time": now_str(),
    }
    append_to_list("points_log.json", log_entry)
    return True, f"消耗 {amount} 积分"


def get_logs(student_id: str, limit: int = 50) -> list[dict]:
    logs = read_json("points_log.json")
    user_logs = [l for l in logs if l["student_id"] == student_id]
    user_logs.sort(key=lambda x: x["time"], reverse=True)
    return user_logs[:limit]


def today_remaining(student_id: str, action: str) -> int | None:
    rule = POINTS_RULES.get(action)
    if not rule or rule["daily_max"] is None:
        return None
    return max(0, rule["daily_max"] - _today_earned(student_id, action))
