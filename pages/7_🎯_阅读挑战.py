"""阅读挑战页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.sidebar import setup_sidebar

from utils.data_io import read_json, write_json
from utils.points_engine import earn_points, get_balance
from utils.time_utils import now_str, this_month_str, today_str

st.set_page_config(page_title="阅读挑战", page_icon="🎯")

setup_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()

sid = st.session_state.student_id
balance = get_balance(sid)

st.title("🎯 阅读挑战")
st.caption(f"当前积分: {balance}")

challenges = read_json("challenges.json")
if not isinstance(challenges, list):
    challenges = []

# 初始化默认挑战
if not challenges:
    month = this_month_str()
    default_challenges = [
        {
            "id": "c1",
            "title": f"{month} 月读3本书",
            "description": "本月内借阅并归还3本不同的书",
            "target": 3,
            "type": "borrow",
            "reward": 50,
            "month": month,
            "participants": {},
        },
        {
            "id": "c2",
            "title": f"{month} 写2篇书评",
            "description": "本月内撰写2篇书评",
            "target": 2,
            "type": "review",
            "reward": 50,
            "month": month,
            "participants": {},
        },
        {
            "id": "c3",
            "title": f"{month} 连续打卡15天",
            "description": "本月内连续打卡15天",
            "target": 15,
            "type": "checkin_streak",
            "reward": 50,
            "month": month,
            "participants": {},
        },
        {
            "id": "c4",
            "title": f"{month} 推荐5本好书",
            "description": "本月内推荐5本好书给其他同学",
            "target": 5,
            "type": "recommend",
            "reward": 50,
            "month": month,
            "participants": {},
        },
    ]
    challenges = default_challenges
    write_json("challenges.json", challenges)

# 计算用户各类行为本月数据
logs = read_json("points_log.json")
month = this_month_str()
month_logs = [l for l in logs if l["student_id"] == sid and l["time"][:7] == month and l["amount"] > 0]

action_counts = {}
for l in month_logs:
    action = l["action"]
    action_counts[action] = action_counts.get(action, 0) + 1

tab_active, tab_completed = st.tabs(["📋 进行中", "✅ 已完成"])

with tab_active:
    active_found = False
    for ch in challenges:
        if ch.get("month", "") != month:
            continue
        participants = ch.get("participants", {})
        my_data = participants.get(sid, {})

        if my_data.get("completed"):
            continue

        active_found = True
        progress = action_counts.get(ch["type"], 0)
        if ch["type"] == "checkin_streak":
            checkin_dates = [l["time"][:10] for l in logs if l["student_id"] == sid and l["action"] == "checkin"]
            from utils.time_utils import streak_days
            progress = streak_days(checkin_dates)

        progress_pct = min(1.0, progress / ch["target"]) if ch["target"] > 0 else 0
        is_joined = sid in participants

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {ch['title']}")
                st.markdown(ch["description"])
                st.progress(progress_pct, text=f"进度: {progress}/{ch['target']}")
                st.caption(f"奖励: +{ch['reward']} 积分 | 参与人数: {len(participants)}")
            with col2:
                if not is_joined:
                    if st.button("参加挑战", key=f"join_{ch['id']}", use_container_width=True):
                        participants[sid] = {"joined_at": now_str(), "completed": False}
                        ch["participants"] = participants
                        write_json("challenges.json", challenges)
                        st.success("已参加挑战！")
                        st.rerun()
                elif progress >= ch["target"]:
                    if st.button("领取奖励", key=f"claim_{ch['id']}", use_container_width=True):
                        ok, msg, pts = earn_points(sid, "challenge", f"完成挑战: {ch['title']}")
                        if ok:
                            participants[sid]["completed"] = True
                            participants[sid]["completed_at"] = now_str()
                            ch["participants"] = participants
                            write_json("challenges.json", challenges)
                            st.success(f"挑战完成！{msg}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.info("已参加，继续加油！")

    if not active_found:
        st.info("暂无进行中的挑战")

with tab_completed:
    completed_found = False
    for ch in challenges:
        participants = ch.get("participants", {})
        my_data = participants.get(sid, {})
        if my_data.get("completed"):
            completed_found = True
            st.success(f"✅ {ch['title']} — 完成于 {my_data.get('completed_at', '')}")

    if not completed_found:
        st.info("暂无已完成的挑战")
