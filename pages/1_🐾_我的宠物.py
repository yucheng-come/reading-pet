"""我的宠物页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.sidebar import setup_sidebar

from utils.pet_engine import get_pet, get_level, next_level, feed, interact, recall, choose_type
from utils.points_engine import get_balance
from assets.pet_art import get_pet_emoji, STATUS_EMOJIS
from config import PET_TYPES, PET_TYPE_NAMES, FEED_COST, FEED_DAILY_MAX, INTERACT_COST, INTERACT_TYPES, RECALL_COST, SHOP_ITEMS

st.set_page_config(page_title="我的宠物", page_icon="🐾")

setup_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()

sid = st.session_state.student_id
pet = get_pet(sid)
level = get_level(pet["growth"])
nxt = next_level(pet["growth"])
balance = get_balance(sid)

st.title("🐾 我的宠物")

# ── 宠物展示区 ──
emoji = get_pet_emoji(pet["type"], level["emoji_key"])
status_emoji = STATUS_EMOJIS.get(pet["status"], "")

# 装备展示
equipped = pet.get("equipped", {})
deco_parts = []
for cat in ["background", "scene", "hat", "scarf"]:
    item_id = equipped.get(cat)
    if item_id:
        item = next((i for i in SHOP_ITEMS if i["id"] == item_id), None)
        if item:
            deco_parts.append(item["emoji"])
deco_str = " ".join(deco_parts)

col_pet, col_info = st.columns([1, 2])
with col_pet:
    st.markdown(f"""
    <div style="text-align:center; font-size:5rem; padding:1rem;">
    {deco_str}<br>{emoji}
    </div>
    """, unsafe_allow_html=True)
    if pet["status"] == "hungry":
        st.warning("😿 宠物饿了！快来喂食吧！")
    elif pet["status"] == "runaway":
        st.error("💨 宠物离家出走了！")

with col_info:
    st.markdown(f"**状态**: {pet['status']} {status_emoji}")
    type_name = PET_TYPE_NAMES.get(pet["type"], "未选择") if pet["type"] else "未选择（Lv.2可选）"
    st.markdown(f"**类型**: {type_name}")
    st.markdown(f"**等级**: Lv.{level['level']} {level['name']}")
    st.markdown(f"**成长值**: {pet['growth']}")
    if nxt:
        progress = (pet["growth"] - level["growth_needed"]) / (nxt["growth_needed"] - level["growth_needed"])
        st.progress(min(1.0, progress), text=f"下一级 Lv.{nxt['level']} {nxt['name']} 需要 {nxt['growth_needed']} 成长值")
    else:
        st.success("已达最高等级！")
    st.markdown(f"**当前积分**: {balance}")
    feeds_left = FEED_DAILY_MAX - pet.get("feeds_today", 0) if pet.get("last_feed_day") == __import__("utils.time_utils", fromlist=["today_str"]).today_str() else FEED_DAILY_MAX
    st.caption(f"今日剩余喂食次数: {feeds_left}/{FEED_DAILY_MAX}")

st.divider()

# ── 选择宠物类型 ──
if level["level"] >= 2 and pet["type"] is None:
    st.subheader("选择宠物类型")
    cols = st.columns(len(PET_TYPES))
    for i, t in enumerate(PET_TYPES):
        with cols[i]:
            emoji_preview = get_pet_emoji(t, "baby")
            if st.button(f"{emoji_preview} {PET_TYPE_NAMES[t]}", key=f"choose_{t}", use_container_width=True):
                ok, msg = choose_type(sid, t)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    st.divider()

# ── 操作区 ──
col_feed, col_interact, col_recall = st.columns(3)

with col_feed:
    st.subheader(f"🍖 喂食 (-{FEED_COST}积分)")
    if st.button("喂食宠物", use_container_width=True):
        ok, msg = feed(sid)
        if ok:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

with col_interact:
    st.subheader(f"🎮 互动 (-{INTERACT_COST}积分)")
    for action in INTERACT_TYPES:
        if st.button(f"{action}", key=f"interact_{action}", use_container_width=True):
            ok, msg = interact(sid, action)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

with col_recall:
    st.subheader(f"📢 召回 (-{RECALL_COST}积分)")
    if pet["status"] == "runaway":
        if st.button("召回宠物", use_container_width=True):
            ok, msg = recall(sid)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    else:
        st.caption("宠物在身边，无需召回")
