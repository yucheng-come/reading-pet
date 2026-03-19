"""宠物养成引擎"""
from utils.data_io import read_json, update_dict
from utils.time_utils import today_str, now_str, days_since
from utils.points_engine import spend_points
from config import (
    PET_LEVELS, PET_TYPES, FEED_COST, FEED_GROWTH, FEED_DAILY_MAX,
    INTERACT_COST, INTERACT_ANIMATIONS, HUNGER_DAYS, RUNAWAY_DAYS, RECALL_COST,
)
import random


def _default_pet(student_id: str) -> dict:
    return {
        "student_id": student_id,
        "type": None,
        "growth": 0,
        "last_feed_date": "",
        "feeds_today": 0,
        "last_feed_day": "",
        "status": "normal",
        "equipped": {"hat": None, "scarf": None, "background": None, "scene": None},
        "created_at": now_str(),
    }


def get_pet(student_id: str) -> dict:
    pets = read_json("pets.json")
    if student_id not in pets:
        pet = _default_pet(student_id)
        pets[student_id] = pet
        from utils.data_io import write_json
        write_json("pets.json", pets)
    pet = pets[student_id]
    _check_hunger(pet)
    return pet


def _save_pet(pet: dict):
    update_dict("pets.json", pet["student_id"], pet)


def get_level(growth: int) -> dict:
    current = PET_LEVELS[0]
    for lv in PET_LEVELS:
        if growth >= lv["growth_needed"]:
            current = lv
    return current


def next_level(growth: int) -> dict | None:
    current = get_level(growth)
    if current["level"] >= 5:
        return None
    return PET_LEVELS[current["level"]]  # next level (0-indexed: level-1 +1)


def _check_hunger(pet: dict):
    if pet["status"] == "runaway":
        return
    days = days_since(pet["last_feed_date"])
    if days >= RUNAWAY_DAYS:
        pet["status"] = "runaway"
        _save_pet(pet)
    elif days >= HUNGER_DAYS:
        pet["status"] = "hungry"
        _save_pet(pet)
    elif pet["status"] == "hungry":
        pet["status"] = "normal"
        _save_pet(pet)


def choose_type(student_id: str, pet_type: str) -> tuple[bool, str]:
    if pet_type not in PET_TYPES:
        return False, "无效的宠物类型"
    pet = get_pet(student_id)
    level = get_level(pet["growth"])
    if level["level"] < 2:
        return False, "宠物还是蛋，达到 Lv.2 才能选择类型"
    if pet["type"] is not None:
        return False, "已经选择过类型了"
    pet["type"] = pet_type
    _save_pet(pet)
    return True, f"选择了 {pet_type} 类型！"


def feed(student_id: str) -> tuple[bool, str]:
    pet = get_pet(student_id)
    if pet["status"] == "runaway":
        return False, "宠物已离家出走，请先召回！"
    today = today_str()
    if pet["last_feed_day"] == today:
        if pet["feeds_today"] >= FEED_DAILY_MAX:
            return False, f"今日喂食已达上限（{FEED_DAILY_MAX}次）"
    else:
        pet["feeds_today"] = 0
        pet["last_feed_day"] = today
    ok, msg = spend_points(student_id, FEED_COST, "喂食宠物")
    if not ok:
        return False, msg
    pet["growth"] += FEED_GROWTH
    pet["feeds_today"] += 1
    pet["last_feed_date"] = today
    pet["status"] = "normal"
    _save_pet(pet)
    level = get_level(pet["growth"])
    return True, f"喂食成功！成长值 +{FEED_GROWTH}（当前 {pet['growth']}，{level['name']} Lv.{level['level']}）"


def interact(student_id: str, action: str) -> tuple[bool, str]:
    pet = get_pet(student_id)
    if pet["status"] == "runaway":
        return False, "宠物已离家出走，请先召回！"
    if action not in INTERACT_ANIMATIONS:
        return False, "无效的互动类型"
    ok, msg = spend_points(student_id, INTERACT_COST, f"宠物{action}")
    if not ok:
        return False, msg
    animation = random.choice(INTERACT_ANIMATIONS[action])
    return True, animation


def recall(student_id: str) -> tuple[bool, str]:
    pet = get_pet(student_id)
    if pet["status"] != "runaway":
        return False, "宠物没有离家出走"
    ok, msg = spend_points(student_id, RECALL_COST, "召回宠物")
    if not ok:
        return False, msg
    pet["status"] = "normal"
    pet["last_feed_date"] = today_str()
    _save_pet(pet)
    return True, "宠物已召回！记得经常喂食哦～"


def equip_item(student_id: str, category: str, item_id: str | None):
    pet = get_pet(student_id)
    pet["equipped"][category] = item_id
    _save_pet(pet)
