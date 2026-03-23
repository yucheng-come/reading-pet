"""个人中心页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.sidebar import setup_sidebar

from utils.auth import get_user, change_password
from utils.points_engine import get_balance, get_logs
from utils.pet_engine import get_pet, get_level
from utils.data_io import read_json
from utils.time_utils import this_month_str
from config import POINTS_RULES

st.set_page_config(page_title="个人中心", page_icon="👤")

setup_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()

sid = st.session_state.student_id
user = get_user(sid)
balance = get_balance(sid)
pet = get_pet(sid)
level = get_level(pet["growth"])

st.title("👤 个人中心")

# ── 个人信息 ──
st.markdown(f"""
<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    border-radius:16px; padding:1.2rem; color:white; margin-bottom:1rem;">
    <div style="font-size:1.3rem; font-weight:700; margin-bottom:0.5rem;">{user['name']}</div>
    <div style="opacity:0.9; font-size:0.9rem;">
        {user['student_id']} · {user['college']} · {user['major']}
    </div>
</div>
""", unsafe_allow_html=True)

# ── 数据概览（2x2）──
logs_all = read_json("points_log.json")
user_logs = [l for l in logs_all if l["student_id"] == sid]
month = this_month_str()
month_earned = sum(l["amount"] for l in user_logs if l["amount"] > 0 and l["time"][:7] == month)
total_earned = sum(l["amount"] for l in user_logs if l["amount"] > 0)
total_spent = abs(sum(l["amount"] for l in user_logs if l["amount"] < 0))

r1 = st.columns(2)
r2 = st.columns(2)
r1[0].metric("当前积分", balance)
r1[1].metric("本月获取", month_earned)
r2[0].metric("累计获取", total_earned)
r2[1].metric("累计消耗", total_spent)

st.divider()

# ── 积分来源统计 ──
st.subheader("📈 积分来源分布")
source_stats = {}
for l in user_logs:
    if l["amount"] > 0:
        action = l["action"]
        label = POINTS_RULES.get(action, {}).get("label", action)
        source_stats[label] = source_stats.get(label, 0) + l["amount"]

if source_stats:
    chart_data = {k: v for k, v in sorted(source_stats.items(), key=lambda x: x[1], reverse=True)}
    for label, pts in chart_data.items():
        pct = pts / total_earned * 100 if total_earned > 0 else 0
        st.markdown(f"**{label}**: {pts}分 ({pct:.1f}%)")
        st.progress(min(1.0, pct / 100))
else:
    st.info("暂无积分记录")

st.divider()

# ── 修改密码 ──
st.subheader("🔒 修改密码")
with st.form("change_pwd"):
    old_pwd = st.text_input("旧密码", type="password")
    new_pwd = st.text_input("新密码", type="password")
    new_pwd2 = st.text_input("确认新密码", type="password")
    if st.form_submit_button("修改密码", use_container_width=True):
        if new_pwd != new_pwd2:
            st.error("两次输入的新密码不一致")
        else:
            ok, msg = change_password(sid, old_pwd, new_pwd)
            if ok:
                st.session_state.logged_in = False
                st.session_state.student_id = ""
                st.session_state.user_name = ""
                st.session_state.is_admin = False
                st.toast(msg + " 即将跳转到登录页面...")
                st.switch_page("app.py")
            else:
                st.error(msg)

st.divider()

# ── 积分明细 ──
st.subheader("📝 积分明细")
recent_logs = get_logs(sid, limit=30)
if recent_logs:
    for l in recent_logs:
        sign = "+" if l["amount"] > 0 else ""
        color = "green" if l["amount"] > 0 else "red"
        st.markdown(f":{color}[{sign}{l['amount']}] {l['note']}  \n<sub>{l['time']}</sub>", unsafe_allow_html=True)
else:
    st.info("暂无积分记录")
