"""书评广场页面"""
import streamlit as st
import sys, os, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.sidebar import setup_sidebar

from utils.data_io import read_json, write_json, append_to_list
from utils.points_engine import earn_points, get_balance
from utils.time_utils import now_str, this_month_str
from config import REVIEW_MIN_LENGTH

st.set_page_config(page_title="书评广场", page_icon="📝")

setup_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()

sid = st.session_state.student_id
balance = get_balance(sid)

st.title("📝 书评广场")
st.caption(f"当前积分: {balance}")

tab_write, tab_browse, tab_best = st.tabs(["✍️ 写书评", "📖 浏览书评", "🏅 月度最佳"])

# ── 写书评 ──
with tab_write:
    st.subheader("撰写书评")
    st.info(f"书评不少于 {REVIEW_MIN_LENGTH} 字，审核通过后可获得 +20 积分")
    with st.form("review_form"):
        book = st.text_input("书名", placeholder="请输入所评图书名称")
        author = st.text_input("作者", placeholder="请输入作者")
        rating = st.slider("评分", 1, 5, 4)
        content = st.text_area("书评内容", placeholder=f"请输入至少{REVIEW_MIN_LENGTH}字的书评...", height=300)
        if st.form_submit_button("提交书评", use_container_width=True):
            if not book.strip():
                st.error("请输入书名")
            elif len(content.strip()) < REVIEW_MIN_LENGTH:
                st.error(f"书评至少 {REVIEW_MIN_LENGTH} 字（当前 {len(content.strip())} 字）")
            else:
                review = {
                    "id": str(uuid.uuid4())[:8],
                    "type": "review",
                    "student_id": sid,
                    "author_name": st.session_state.user_name,
                    "book": book.strip(),
                    "book_author": author.strip(),
                    "rating": rating,
                    "content": content.strip(),
                    "votes": 0,
                    "voted_by": [],
                    "status": "pending",
                    "time": now_str(),
                }
                append_to_list("reviews.json", review)
                ok, msg, pts = earn_points(sid, "review", f"书评《{book}》")
                if ok:
                    st.success(f"书评已提交！{msg}")
                else:
                    st.success("书评已提交！")
                    st.warning(msg)
                st.rerun()

# ── 浏览书评 ──
with tab_browse:
    reviews = read_json("reviews.json")
    book_reviews = [r for r in reviews if r.get("type") == "review"]
    book_reviews.sort(key=lambda x: x.get("time", ""), reverse=True)

    if not book_reviews:
        st.info("暂无书评，快来写第一篇吧！")
    else:
        for r in book_reviews:
            status_badge = {"pending": "🔵 待审核", "approved": "✅ 已通过", "rejected": "❌ 未通过"}.get(r.get("status"), "")
            with st.expander(f"📕 《{r['book']}》 {'⭐' * r.get('rating', 0)} — {r.get('author_name', '匿名')} {status_badge}"):
                st.markdown(f"**作者**: {r.get('book_author', '未知')}")
                st.markdown(f"**时间**: {r.get('time', '')}")
                st.markdown(r.get("content", ""))
                st.markdown(f"👍 {r.get('votes', 0)} 票")
                # 投票
                if r.get("student_id") != sid and sid not in r.get("voted_by", []):
                    if st.button(f"👍 点赞", key=f"vote_{r['id']}"):
                        for rev in reviews:
                            if rev.get("id") == r["id"]:
                                rev["votes"] = rev.get("votes", 0) + 1
                                rev.setdefault("voted_by", []).append(sid)
                                break
                        write_json("reviews.json", reviews)
                        st.success("点赞成功！")
                        st.rerun()
                elif r.get("student_id") == sid:
                    st.caption("这是你的书评")
                else:
                    st.caption("已点赞")

# ── 月度最佳 ──
with tab_best:
    reviews = read_json("reviews.json")
    month = this_month_str()
    month_reviews = [r for r in reviews if r.get("type") == "review" and r.get("time", "")[:7] == month and r.get("status") == "approved"]
    month_reviews.sort(key=lambda x: x.get("votes", 0), reverse=True)

    st.subheader(f"🏅 {month} 月度最佳书评")
    if not month_reviews:
        st.info("本月暂无已通过的书评")
    else:
        for i, r in enumerate(month_reviews[:10]):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"{medal} 《{r['book']}》— {r.get('author_name', '匿名')} | 👍 {r.get('votes', 0)}票")
