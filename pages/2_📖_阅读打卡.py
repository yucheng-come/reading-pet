"""阅读打卡页面"""
import streamlit as st
import sys, os, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.sidebar import setup_sidebar

from utils.points_engine import earn_points, get_balance, today_remaining
from utils.data_io import read_json, append_to_list
from utils.time_utils import today_str, now_str, streak_days
from config import POINTS_RULES

st.set_page_config(page_title="阅读打卡", page_icon="📖")

setup_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()

sid = st.session_state.student_id
balance = get_balance(sid)

st.title("📖 阅读打卡")

# ── 今日额度概览（2x2 网格适配手机）──
actions = ["checkin", "borrow", "return", "recommend"]
row1 = st.columns(2)
row2 = st.columns(2)
all_cols = [row1[0], row1[1], row2[0], row2[1]]
for i, action in enumerate(actions):
    rule = POINTS_RULES[action]
    remaining = today_remaining(sid, action)
    with all_cols[i]:
        st.metric(rule["label"], f"+{rule['points']}分/次", f"剩余 {remaining}分")

st.divider()

# ── 阅读签到 ──
st.subheader("✅ 每日签到")
logs = read_json("points_log.json")
checkin_dates = [l["time"][:10] for l in logs if l["student_id"] == sid and l["action"] == "checkin"]
streak = streak_days(checkin_dates)
st.info(f"连续打卡天数: **{streak}** 天 {'🔥' * min(streak, 10)}")

already_checkin = today_str() in checkin_dates
if already_checkin:
    st.success("今日已签到 ✅")
else:
    if st.button("立即签到", use_container_width=True):
        ok, msg, pts = earn_points(sid, "checkin", f"阅读签到 {today_str()}")
        if ok:
            st.toast(msg)
            # 检查连续7天奖励
            new_checkin_dates = checkin_dates + [today_str()]
            new_streak = streak_days(new_checkin_dates)
            if new_streak > 0 and new_streak % 7 == 0:
                earn_points(sid, "streak_7", f"连续{new_streak}天打卡奖励")
                st.balloons()
                st.toast("连续7天打卡奖励 +10积分！")
            st.rerun()
        else:
            st.error(msg)

st.divider()

# ── 借阅图书（提交审核） ──
st.subheader("📚 借阅图书")
with st.form("borrow_form"):
    book_name = st.text_input("书名", placeholder="请输入借阅的书名")
    if st.form_submit_button("提交借阅记录", use_container_width=True):
        if not book_name.strip():
            st.error("请输入书名")
        else:
            append_to_list("borrow_requests.json", {
                "id": str(uuid.uuid4())[:8],
                "student_id": sid,
                "name": st.session_state.user_name,
                "book": book_name.strip(),
                "action": "borrow",
                "status": "pending",
                "time": now_str(),
            })
            st.toast("借阅记录已提交，等待审核通过后获得积分")
            st.rerun()

# ── 归还图书（提交审核） ──
st.subheader("📕 归还图书")
with st.form("return_form"):
    ret_book = st.text_input("书名", placeholder="请输入归还的书名", key="ret_book")
    if st.form_submit_button("提交归还记录", use_container_width=True):
        if not ret_book.strip():
            st.error("请输入书名")
        else:
            append_to_list("borrow_requests.json", {
                "id": str(uuid.uuid4())[:8],
                "student_id": sid,
                "name": st.session_state.user_name,
                "book": ret_book.strip(),
                "action": "return",
                "status": "pending",
                "time": now_str(),
            })
            st.toast("归还记录已提交，等待审核通过后获得积分")
            st.rerun()

# ── 我的借阅审核状态 ──
borrow_requests = read_json("borrow_requests.json")
my_requests = [r for r in borrow_requests if r.get("student_id") == sid]
if my_requests:
    my_requests.sort(key=lambda x: x.get("time", ""), reverse=True)
    pending_count = sum(1 for r in my_requests if r.get("status") == "pending")
    if pending_count > 0:
        st.caption(f"📋 你有 {pending_count} 条借还记录待审核")

    with st.expander(f"查看借还记录（近20条）"):
        for r in my_requests[:20]:
            action_cn = "📗 借阅" if r.get("action") == "borrow" else "📕 归还"
            status_badge = {"pending": "🔵 待审核", "approved": "✅ 已通过", "rejected": "❌ 未通过"}.get(r.get("status"), "")
            st.markdown(f"{action_cn} 《{r.get('book', '')}》 {status_badge}  \n<sub>{r.get('time', '')}</sub>", unsafe_allow_html=True)

st.divider()

# ── 推荐好书 ──
st.subheader("💡 推荐好书")
with st.form("recommend_form"):
    rec_book = st.text_input("推荐书名", placeholder="你想推荐什么书？")
    rec_reason = st.text_area("推荐理由", placeholder="简单说说推荐理由", height=100)
    if st.form_submit_button("提交推荐", use_container_width=True):
        if not rec_book.strip():
            st.error("请输入书名")
        else:
            ok, msg, pts = earn_points(sid, "recommend", f"推荐《{rec_book}》")
            if ok:
                append_to_list("reviews.json", {
                    "type": "recommend",
                    "student_id": sid,
                    "book": rec_book,
                    "content": rec_reason,
                    "time": now_str(),
                })
                st.toast(msg)
                st.rerun()
            else:
                st.error(msg)
