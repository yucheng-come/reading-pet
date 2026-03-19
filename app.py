"""悦读养成记 — 入口：登录 / 注册"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.auth import login, register

st.set_page_config(
    page_title="悦读养成记",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── session 初始化 ──
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_id = ""
    st.session_state.user_name = ""
    st.session_state.is_admin = False


def do_logout():
    st.session_state.logged_in = False
    st.session_state.student_id = ""
    st.session_state.user_name = ""
    st.session_state.is_admin = False


# ── 已登录 ──
if st.session_state.logged_in:
    st.sidebar.success(f"已登录：{st.session_state.user_name}（{st.session_state.student_id}）")
    if st.sidebar.button("退出登录"):
        do_logout()
        st.rerun()

    st.title("📚 悦读养成记")
    st.markdown("### 欢迎回来！请从左侧菜单选择功能 👈")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🐾 **我的宠物**\n\n喂食、互动、装扮你的阅读小伙伴")
    with col2:
        st.info("📖 **阅读打卡**\n\n记录每日阅读，赚取积分")
    with col3:
        st.info("🏆 **排行榜**\n\n看看谁是最佳读者")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.info("📝 **书评广场**\n\n分享读书感悟")
    with col5:
        st.info("🛍️ **装扮商店**\n\n用积分装扮你的宠物")
    with col6:
        st.info("🎯 **阅读挑战**\n\n完成挑战赢取大量积分")

else:
    # ── 未登录 ──
    st.title("📚 悦读养成记")
    st.markdown("*阅读积分养宠物 — 让阅读成为习惯*")
    st.divider()

    tab_login, tab_register = st.tabs(["🔑 登录", "📝 注册"])

    with tab_login:
        with st.form("login_form"):
            sid = st.text_input("学号", placeholder="请输入学号")
            pwd = st.text_input("密码", type="password", placeholder="初始密码为身份证后八位")
            submit = st.form_submit_button("登录", use_container_width=True)
            if submit:
                ok, msg = login(sid, pwd)
                if ok:
                    from utils.auth import get_user
                    user = get_user(sid)
                    st.session_state.logged_in = True
                    st.session_state.student_id = sid
                    st.session_state.user_name = user["name"]
                    st.session_state.is_admin = user.get("is_admin", False)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_register:
        with st.form("register_form"):
            r_sid = st.text_input("学号", placeholder="请输入学号", key="r_sid")
            r_name = st.text_input("姓名", placeholder="请输入姓名")
            r_college = st.text_input("学院", placeholder="请输入学院")
            r_major = st.text_input("专业", placeholder="请输入专业")
            r_pwd = st.text_input("密码（身份证后八位）", type="password", placeholder="请输入身份证后八位作为初始密码")
            r_submit = st.form_submit_button("注册", use_container_width=True)
            if r_submit:
                ok, msg = register(r_sid, r_name, r_college, r_major, r_pwd)
                if ok:
                    st.success(msg + " 请切换到登录标签页登录。")
                else:
                    st.error(msg)
