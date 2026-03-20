"""好友圈页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.sidebar import setup_sidebar

from utils.data_io import read_json, write_json
from utils.auth import get_user
from utils.points_engine import get_balance, spend_points, earn_points
from utils.pet_engine import get_pet, get_level
from assets.pet_art import get_pet_emoji
from utils.time_utils import now_str, today_str
from config import GIFT_COST, GIFT_RECEIVE, PET_TYPE_NAMES

st.set_page_config(page_title="好友圈", page_icon="👥")

setup_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()

sid = st.session_state.student_id
balance = get_balance(sid)

st.title("👥 好友圈")
st.caption(f"当前积分: {balance}")

# 读取好友数据
friends_data = read_json("friends.json")
if not isinstance(friends_data, dict):
    friends_data = {}
my_friends = friends_data.get(sid, [])

tab_add, tab_list, tab_gift = st.tabs(["➕ 添加好友", "👥 好友列表", "🎁 送礼物"])

# ── 添加好友 ──
with tab_add:
    st.subheader("添加好友")
    with st.form("add_friend"):
        friend_id = st.text_input("好友学号", placeholder="请输入好友的学号")
        if st.form_submit_button("添加好友", use_container_width=True):
            if not friend_id.strip():
                st.error("请输入学号")
            elif friend_id == sid:
                st.error("不能添加自己为好友")
            elif friend_id in my_friends:
                st.error("已经是好友了")
            else:
                friend_user = get_user(friend_id)
                if not friend_user:
                    st.error("该学号不存在")
                elif friend_user.get("is_admin"):
                    st.error("不能添加管理员为好友")
                else:
                    my_friends.append(friend_id)
                    friends_data[sid] = my_friends
                    # 双向添加
                    other_friends = friends_data.get(friend_id, [])
                    if sid not in other_friends:
                        other_friends.append(sid)
                        friends_data[friend_id] = other_friends
                    write_json("friends.json", friends_data)
                    st.success(f"已添加 {friend_user['name']} 为好友！")
                    st.rerun()

# ── 好友列表 ──
with tab_list:
    st.subheader("我的好友")
    if not my_friends:
        st.info("还没有好友，快去添加吧！")
    else:
        for fid in my_friends:
            friend_user = get_user(fid)
            if not friend_user:
                continue
            friend_pet = get_pet(fid)
            friend_level = get_level(friend_pet["growth"])
            friend_emoji = get_pet_emoji(friend_pet["type"], friend_level["emoji_key"])
            type_name = PET_TYPE_NAMES.get(friend_pet["type"], "未选择") if friend_pet["type"] else "未选择"

            with st.expander(f"{friend_emoji} {friend_user['name']} ({fid}) — Lv.{friend_level['level']} {friend_level['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**学院**: {friend_user['college']}")
                    st.markdown(f"**宠物类型**: {type_name}")
                with col2:
                    st.markdown(f"**成长值**: {friend_pet['growth']}")
                    st.markdown(f"**状态**: {friend_pet['status']}")
                # 删除好友
                if st.button(f"删除好友", key=f"del_{fid}"):
                    my_friends.remove(fid)
                    friends_data[sid] = my_friends
                    # 双向删除
                    other_friends = friends_data.get(fid, [])
                    if sid in other_friends:
                        other_friends.remove(sid)
                        friends_data[fid] = other_friends
                    write_json("friends.json", friends_data)
                    st.rerun()

# ── 送礼物 ──
with tab_gift:
    st.subheader(f"🎁 送礼物（花费 {GIFT_COST} 积分，双方各得 {GIFT_RECEIVE} 积分）")
    if not my_friends:
        st.info("先添加好友才能送礼物哦")
    else:
        # 检查今日是否已送过
        logs = read_json("points_log.json")
        today = today_str()
        today_gifts = [l for l in logs if l["student_id"] == sid and l["action"] == "spend" and "送礼" in l.get("note", "") and l["time"][:10] == today]

        for fid in my_friends:
            friend_user = get_user(fid)
            if not friend_user:
                continue
            already_gifted = any(fid in l.get("note", "") for l in today_gifts)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{friend_user['name']}** ({fid})")
            with col2:
                if already_gifted:
                    st.caption("今日已送")
                else:
                    if st.button(f"送礼", key=f"gift_{fid}"):
                        ok, msg = spend_points(sid, GIFT_COST, f"送礼给 {fid}")
                        if ok:
                            # 双方各得积分（直接记录正积分）
                            from utils.data_io import append_to_list
                            import uuid
                            for target_id in [sid, fid]:
                                append_to_list("points_log.json", {
                                    "id": str(uuid.uuid4())[:8],
                                    "student_id": target_id,
                                    "action": "gift_bonus",
                                    "amount": GIFT_RECEIVE,
                                    "note": f"好友互赠奖励",
                                    "time": now_str(),
                                })
                            st.success(f"送礼成功！你和 {friend_user['name']} 各得 {GIFT_RECEIVE} 积分")
                            st.rerun()
                        else:
                            st.error(msg)
