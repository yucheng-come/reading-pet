"""侧边栏公共组件：退出登录 + 隐藏管理后台"""
import streamlit as st


def setup_sidebar():
    """在每个页面调用，设置侧边栏退出按钮并对非管理员隐藏管理后台"""
    if st.session_state.get("logged_in"):
        st.sidebar.markdown(f"**{st.session_state.user_name}**（{st.session_state.student_id}）")
        if st.sidebar.button("🚪 退出登录", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.student_id = ""
            st.session_state.user_name = ""
            st.session_state.is_admin = False
            st.switch_page("app.py")

    # 非管理员隐藏管理后台入口
    if not st.session_state.get("is_admin"):
        st.markdown("""
        <style>
        [data-testid="stSidebarNav"] li:last-child { display: none; }
        </style>
        """, unsafe_allow_html=True)
