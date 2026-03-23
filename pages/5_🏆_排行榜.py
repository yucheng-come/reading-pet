"""排行榜页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.sidebar import setup_sidebar

from utils.ranking_engine import get_personal_ranking, get_college_ranking

st.set_page_config(page_title="排行榜", page_icon="🏆")

setup_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()

sid = st.session_state.student_id

st.title("🏆 排行榜")

tab_personal, tab_college = st.tabs(["👤 个人排行", "🏫 学院排行"])

with tab_personal:
    st.subheader(f"个人积分排行榜")
    ranking = get_personal_ranking()
    if not ranking:
        st.info("暂无数据")
    else:
        # 找到当前用户排名
        my_rank = next((i+1 for i, r in enumerate(ranking) if r["student_id"] == sid), None)
        if my_rank:
            st.success(f"你的排名: 第 {my_rank} 名")

        for i, r in enumerate(ranking):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            is_me = r["student_id"] == sid
            bg = "linear-gradient(135deg,#fff3cd,#ffe082)" if is_me else "#f8f9fa"
            border = "2px solid #ffc107" if is_me else "1px solid #e0e0e0"
            me_tag = " ⬅️" if is_me else ""
            st.markdown(f"""
            <div style="background:{bg}; border:{border}; border-radius:12px;
                padding:0.6rem 0.8rem; margin-bottom:0.4rem; font-size:0.95rem;">
                <b>{medal}</b> {r["name"]} <span style="color:#888;">({r["college"]})</span>{me_tag}<br>
                <span style="font-size:0.85rem; color:#555;">总积分 {r["total_points"]} · 本月 {r["month_points"]}</span>
            </div>
            """, unsafe_allow_html=True)

with tab_college:
    st.subheader("学院积分排行榜")
    ranking = get_college_ranking()
    if not ranking:
        st.info("暂无数据")
    else:
        for i, r in enumerate(ranking):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"""
            <div style="background:#f8f9fa; border:1px solid #e0e0e0; border-radius:12px;
                padding:0.6rem 0.8rem; margin-bottom:0.4rem; font-size:0.95rem;">
                <b>{medal} {r['college']}</b><br>
                <span style="font-size:0.85rem; color:#555;">总积分 {r['total_points']} · {r['members']}人 · 人均 {r['avg_points']}</span>
            </div>
            """, unsafe_allow_html=True)
