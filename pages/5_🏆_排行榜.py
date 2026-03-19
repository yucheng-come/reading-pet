"""排行榜页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.ranking_engine import get_personal_ranking, get_college_ranking
from utils.time_utils import this_month_str

st.set_page_config(page_title="排行榜", page_icon="🏆")

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
            is_me = " ⬅️ 你" if r["student_id"] == sid else ""
            highlight = "background-color: #fff3cd; padding: 4px; border-radius: 4px;" if r["student_id"] == sid else ""
            st.markdown(
                f'<div style="{highlight}">{medal} <b>{r["name"]}</b> ({r["college"]}) — '
                f'总积分: {r["total_points"]} | 本月: {r["month_points"]}{is_me}</div>',
                unsafe_allow_html=True
            )

with tab_college:
    st.subheader("学院积分排行榜")
    ranking = get_college_ranking()
    if not ranking:
        st.info("暂无数据")
    else:
        for i, r in enumerate(ranking):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(
                f"{medal} **{r['college']}** — 总积分: {r['total_points']} | "
                f"成员: {r['members']}人 | 人均: {r['avg_points']}分"
            )
