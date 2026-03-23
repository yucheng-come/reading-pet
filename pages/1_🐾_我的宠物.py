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

equipped = pet.get("equipped", {})
deco_parts = []
for cat in ["background", "scene", "hat", "scarf"]:
    item_id = equipped.get(cat)
    if item_id:
        item = next((i for i in SHOP_ITEMS if i["id"] == item_id), None)
        if item:
            deco_parts.append(item["emoji"])
deco_str = " ".join(deco_parts)

# 宠物卡片：上方展示，下方信息
st.markdown(f"""
<div style="text-align:center; background:linear-gradient(135deg,#e0c3fc 0%,#8ec5fc 100%);
    border-radius:20px; padding:1.5rem 1rem; margin-bottom:1rem;">
    <div style="font-size:1.2rem; margin-bottom:0.3rem;">{deco_str}</div>
    <div style="font-size:5rem; line-height:1.2;">{emoji}</div>
    <div style="margin-top:0.5rem; font-size:1.1rem; font-weight:600; color:#333;">
        Lv.{level['level']} {level['name']} {status_emoji}
    </div>
</div>
""", unsafe_allow_html=True)

if pet["status"] == "hungry":
    st.warning("😿 宠物饿了！快来喂食吧！")
elif pet["status"] == "runaway":
    st.error("💨 宠物离家出走了！")

# 信息区
from utils.time_utils import today_str
type_name = PET_TYPE_NAMES.get(pet["type"], "未选择") if pet["type"] else "未选择（Lv.2可选）"
feeds_left = FEED_DAILY_MAX - pet.get("feeds_today", 0) if pet.get("last_feed_day") == today_str() else FEED_DAILY_MAX

col1, col2, col3 = st.columns(3)
col1.metric("积分", balance)
col2.metric("成长值", pet["growth"])
col3.metric("今日喂食", f"{feeds_left}/{FEED_DAILY_MAX}")

if nxt:
    progress = (pet["growth"] - level["growth_needed"]) / (nxt["growth_needed"] - level["growth_needed"])
    st.progress(min(1.0, progress), text=f"下一级 Lv.{nxt['level']} {nxt['name']} 需要 {nxt['growth_needed']}")
else:
    st.success("已达最高等级！")

st.markdown(f"**类型**: {type_name}")

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

# ── 操作区：竖排更适合手机 ──
st.subheader("操作")

col_a, col_b = st.columns(2)
with col_a:
    if st.button(f"🍖 喂食 (-{FEED_COST}积分)", use_container_width=True):
        ok, msg = feed(sid)
        if ok:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)
with col_b:
    if pet["status"] == "runaway":
        if st.button(f"📢 召回 (-{RECALL_COST}积分)", use_container_width=True):
            ok, msg = recall(sid)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    else:
        st.button("📢 召回（无需）", use_container_width=True, disabled=True)

col_c, col_d = st.columns(2)
for idx, action in enumerate(INTERACT_TYPES):
    with [col_c, col_d][idx]:
        if st.button(f"🎮 {action} (-{INTERACT_COST}积分)", key=f"interact_{action}", use_container_width=True):
            ok, msg = interact(sid, action)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
