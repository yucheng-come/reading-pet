"""悦读养成记 — 全局配置常量"""

import os

# === 路径 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# === 管理员 ===
ADMIN_ACCOUNTS = [
    {"student_id": "admin001", "name": "管理员A", "college": "图书馆", "major": "系统管理", "password_raw": "admin888"},
    {"student_id": "admin002", "name": "管理员B", "college": "图书馆", "major": "系统管理", "password_raw": "admin888"},
    {"student_id": "admin003", "name": "管理员C", "college": "图书馆", "major": "系统管理", "password_raw": "admin888"},
]

# === 宠物等级 ===
PET_LEVELS = [
    {"level": 1, "name": "蛋",  "growth_needed": 0,    "emoji_key": "egg"},
    {"level": 2, "name": "幼崽", "growth_needed": 100,  "emoji_key": "baby"},
    {"level": 3, "name": "少年", "growth_needed": 500,  "emoji_key": "teen"},
    {"level": 4, "name": "成年", "growth_needed": 1500, "emoji_key": "adult"},
    {"level": 5, "name": "传说", "growth_needed": 5000, "emoji_key": "legend"},
]

PET_TYPES = ["cat", "dog", "dragon"]
PET_TYPE_NAMES = {"cat": "猫咪", "dog": "狗狗", "dragon": "龙宝"}

# === 宠物互动 ===
FEED_COST = 10          # 喂食花费积分
FEED_GROWTH = 10        # 喂食获得成长值
FEED_DAILY_MAX = 3      # 每日喂食上限

INTERACT_COST = 5       # 互动花费积分
INTERACT_TYPES = ["玩耍", "洗澡"]
INTERACT_ANIMATIONS = {
    "玩耍": ["🎾 扔球接球！", "🧶 追毛线团！", "🪁 一起放风筝！", "🎭 表演杂技！"],
    "洗澡": ["🫧 泡泡浴时间～", "🚿 冲冲更健康！", "🧴 涂上香香的沐浴露～", "🛁 在浴缸里扑腾！"],
}

HUNGER_DAYS = 3         # 几天不喂进入饥饿
RUNAWAY_DAYS = 7        # 几天不喂离家出走
RECALL_COST = 50        # 召回花费积分

# === 积分规则 ===
POINTS_RULES = {
    "borrow":     {"points": 10, "daily_max": 30,   "label": "借阅图书"},
    "return":     {"points": 5,  "daily_max": 15,   "label": "归还图书"},
    "checkin":    {"points": 5,  "daily_max": 5,    "label": "阅读打卡"},
    "review":     {"points": 20, "daily_max": 40,   "label": "撰写书评"},
    "activity":   {"points": 30, "daily_max": 30,   "label": "参加活动"},
    "recommend":  {"points": 10, "daily_max": 20,   "label": "推荐好书"},
    "challenge":  {"points": 50, "daily_max": None, "label": "完成挑战"},
    "streak_7":   {"points": 10, "daily_max": None, "label": "连续7天打卡"},
}

# === 装扮商店 ===
SHOP_ITEMS = [
    {"id": "hat_scholar",   "name": "学士帽",   "category": "hat",    "price": 50,  "emoji": "🎓"},
    {"id": "hat_crown",     "name": "皇冠",     "category": "hat",    "price": 200, "emoji": "👑"},
    {"id": "hat_flower",    "name": "花环",     "category": "hat",    "price": 30,  "emoji": "💐"},
    {"id": "hat_party",     "name": "派对帽",   "category": "hat",    "price": 40,  "emoji": "🎉"},
    {"id": "scarf_red",     "name": "红围巾",   "category": "scarf",  "price": 40,  "emoji": "🧣"},
    {"id": "scarf_rainbow", "name": "彩虹围巾", "category": "scarf",  "price": 80,  "emoji": "🌈"},
    {"id": "scarf_bow",     "name": "蝴蝶结",   "category": "scarf",  "price": 35,  "emoji": "🎀"},
    {"id": "bg_garden",     "name": "花园背景", "category": "background", "price": 100, "emoji": "🌸"},
    {"id": "bg_space",      "name": "星空背景", "category": "background", "price": 150, "emoji": "🌌"},
    {"id": "bg_ocean",      "name": "海洋背景", "category": "background", "price": 120, "emoji": "🌊"},
    {"id": "bg_library",    "name": "书房背景", "category": "background", "price": 80,  "emoji": "📚"},
    {"id": "scene_rain",    "name": "下雨场景", "category": "scene",  "price": 60,  "emoji": "🌧️"},
    {"id": "scene_snow",    "name": "下雪场景", "category": "scene",  "price": 60,  "emoji": "❄️"},
    {"id": "scene_sakura",  "name": "樱花场景", "category": "scene",  "price": 90,  "emoji": "🌸"},
]

CATEGORY_NAMES = {
    "hat": "帽子",
    "scarf": "围巾/配饰",
    "background": "背景",
    "scene": "场景",
}

# === 好友 ===
GIFT_COST = 20          # 送礼花费
GIFT_RECEIVE = 5        # 双方各得

# === 书评 ===
REVIEW_MIN_LENGTH = 200  # 书评最少字数
