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

# ── 预加载借阅数据（用于去重判断） ──
borrow_requests = read_json("borrow_requests.json")
if not isinstance(borrow_requests, list):
    borrow_requests = []
my_requests = [r for r in borrow_requests if r.get("student_id") == sid]

# 提取当前未归还的书（已借阅且未被归还通过的书名）
my_borrowed_books = set()
my_returned_books = set()
for r in my_requests:
    book = r.get("book", "")
    if r["action"] == "borrow" and r["status"] != "rejected":
        my_borrowed_books.add(book)
    elif r["action"] == "return" and r["status"] != "rejected":
        my_returned_books.add(book)
# 当前持有中的书 = 借了但没还的
my_holding_books = my_borrowed_books - my_returned_books
# 已提交过借阅的书（含待审核和已通过，排除已拒绝）
my_active_borrow = {r["book"] for r in my_requests if r["action"] == "borrow" and r["status"] != "rejected"}
my_active_return = {r["book"] for r in my_requests if r["action"] == "return" and r["status"] != "rejected"}

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
        elif book_name.strip() in my_active_borrow:
            st.error(f"《{book_name.strip()}》已提交过借阅记录，不可重复提交")
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
if not my_holding_books:
    st.caption("暂无在借图书")
with st.form("return_form"):
    ret_book = st.text_input("书名", placeholder="请输入归还的书名", key="ret_book")
    if st.form_submit_button("提交归还记录", use_container_width=True):
        if not ret_book.strip():
            st.error("请输入书名")
        elif ret_book.strip() not in my_holding_books:
            if ret_book.strip() in my_active_return:
                st.error(f"《{ret_book.strip()}》已提交过归还记录")
            else:
                st.error(f"《{ret_book.strip()}》不在你的借阅记录中，请先提交借阅")
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
if my_requests:
    my_requests_sorted = sorted(my_requests, key=lambda x: x.get("time", ""), reverse=True)
    pending_count = sum(1 for r in my_requests if r.get("status") == "pending")
    if pending_count > 0:
        st.caption(f"📋 你有 {pending_count} 条借还记录待审核")

    with st.expander(f"查看借还记录（近20条）"):
        for r in my_requests_sorted[:20]:
            action_cn = "📗 借阅" if r.get("action") == "borrow" else "📕 归还"
            status_badge = {"pending": "🔵 待审核", "approved": "✅ 已通过", "rejected": "❌ 未通过"}.get(r.get("status"), "")
            st.markdown(f"{action_cn} 《{r.get('book', '')}》 {status_badge}  \n<sub>{r.get('time', '')}</sub>", unsafe_allow_html=True)

st.divider()

# ── 推荐好书（提交审核） ──
st.subheader("💡 推荐好书")

# 读取已有推荐
reviews = read_json("reviews.json")
my_recommends = [r for r in reviews if r.get("type") == "recommend" and r.get("student_id") == sid]
my_recommend_books = {r.get("book", "") for r in my_recommends}

with st.form("recommend_form"):
    rec_book = st.text_input("推荐书名", placeholder="你想推荐什么书？")
    rec_reason = st.text_area("推荐理由", placeholder="简单说说推荐理由", height=100)
    if st.form_submit_button("提交推荐", use_container_width=True):
        if not rec_book.strip():
            st.error("请输入书名")
        elif rec_book.strip() in my_recommend_books:
            st.error(f"你已推荐过《{rec_book.strip()}》，不可重复推荐")
        else:
            append_to_list("reviews.json", {
                "id": str(uuid.uuid4())[:8],
                "type": "recommend",
                "student_id": sid,
                "author_name": st.session_state.user_name,
                "book": rec_book.strip(),
                "content": rec_reason.strip(),
                "status": "pending",
                "time": now_str(),
            })
            st.toast("推荐已提交，等待审核通过后获得积分")
            st.rerun()

# ── 我的推荐审核状态 ──
if my_recommends:
    my_recs_sorted = sorted(my_recommends, key=lambda x: x.get("time", ""), reverse=True)
    rec_pending = sum(1 for r in my_recommends if r.get("status") == "pending")
    if rec_pending > 0:
        st.caption(f"📋 你有 {rec_pending} 条推荐待审核")

    with st.expander(f"查看推荐记录（近10条）"):
        for r in my_recs_sorted[:10]:
            status_badge = {"pending": "🔵 待审核", "approved": "✅ 已通过", "rejected": "❌ 未通过"}.get(r.get("status"), "🔵 待审核")
            st.markdown(f"💡 《{r.get('book', '')}》 {status_badge}  \n<sub>{r.get('time', '')}</sub>", unsafe_allow_html=True)
