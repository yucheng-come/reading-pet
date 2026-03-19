"""时间工具函数"""
from datetime import datetime, date


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str() -> str:
    return date.today().isoformat()


def days_since(date_str: str) -> int:
    if not date_str:
        return 0
    try:
        past = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        return (date.today() - past).days
    except (ValueError, TypeError):
        return 0


def this_month_str() -> str:
    return date.today().strftime("%Y-%m")


def streak_days(checkin_dates: list[str]) -> int:
    """计算从今天往回的连续打卡天数"""
    if not checkin_dates:
        return 0
    sorted_dates = sorted(set(checkin_dates), reverse=True)
    today = date.today()
    streak = 0
    for i, d in enumerate(sorted_dates):
        try:
            dt = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            break
        expected = today - __import__("datetime").timedelta(days=i)
        if dt == expected:
            streak += 1
        else:
            break
    return streak
