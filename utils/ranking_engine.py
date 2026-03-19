"""排行榜计算引擎"""
from utils.data_io import read_json
from utils.time_utils import this_month_str


def get_personal_ranking(top_n: int = 50) -> list[dict]:
    logs = read_json("points_log.json")
    users = read_json("users.json")
    month = this_month_str()

    totals = {}
    month_totals = {}
    for l in logs:
        sid = l["student_id"]
        if l["amount"] > 0:
            totals[sid] = totals.get(sid, 0) + l["amount"]
            if l["time"][:7] == month:
                month_totals[sid] = month_totals.get(sid, 0) + l["amount"]

    ranking = []
    for sid, total in sorted(totals.items(), key=lambda x: x[1], reverse=True)[:top_n]:
        user = users.get(sid, {})
        if user.get("is_admin"):
            continue
        ranking.append({
            "student_id": sid,
            "name": user.get("name", "未知"),
            "college": user.get("college", ""),
            "total_points": total,
            "month_points": month_totals.get(sid, 0),
        })
    return ranking


def get_college_ranking() -> list[dict]:
    logs = read_json("points_log.json")
    users = read_json("users.json")

    college_totals = {}
    college_members = {}
    for l in logs:
        sid = l["student_id"]
        user = users.get(sid, {})
        if user.get("is_admin"):
            continue
        college = user.get("college", "未知")
        if l["amount"] > 0:
            college_totals[college] = college_totals.get(college, 0) + l["amount"]
            college_members.setdefault(college, set()).add(sid)

    ranking = []
    for college, total in sorted(college_totals.items(), key=lambda x: x[1], reverse=True):
        members = len(college_members.get(college, set()))
        ranking.append({
            "college": college,
            "total_points": total,
            "members": members,
            "avg_points": round(total / members, 1) if members > 0 else 0,
        })
    return ranking
