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

# ── 自定义样式 ──
st.markdown("""
<style>
/* 登录页整体背景 */
[data-testid="stMain"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}
/* 登录卡片 */
.login-card {
    background: white;
    border-radius: 20px;
    padding: 2.5rem 2rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    max-width: 460px;
    margin: 0 auto;
}
.login-header {
    text-align: center;
    margin-bottom: 1.5rem;
}
.login-header h1 {
    font-size: 2.2rem;
    margin: 0;
    color: #333;
}
.login-header .pet-icon {
    font-size: 4rem;
    display: block;
    margin-bottom: 0.5rem;
}
.login-header .subtitle {
    color: #888;
    font-size: 1rem;
    margin-top: 0.3rem;
}
/* 功能卡片 */
.feature-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    height: 100%;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}
.feature-card .icon {
    font-size: 2.5rem;
    display: block;
    margin-bottom: 0.5rem;
}
.feature-card .title {
    font-weight: 700;
    font-size: 1.1rem;
    color: #333;
}
.feature-card .desc {
    color: #888;
    font-size: 0.85rem;
    margin-top: 0.3rem;
}
/* 欢迎横幅 */
.welcome-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 2rem;
    color: white;
    text-align: center;
    margin-bottom: 1.5rem;
}
.welcome-banner h2 {
    margin: 0;
    font-size: 1.8rem;
}
.welcome-banner p {
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

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

    st.markdown(f"""
    <div class="welcome-banner">
        <h2>欢迎回来，{st.session_state.user_name}！</h2>
        <p>从左侧菜单选择功能，开始你的阅读之旅</p>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("🐾", "我的宠物", "喂食、互动、装扮你的阅读小伙伴"),
        ("📖", "阅读打卡", "记录每日阅读，赚取积分"),
        ("🏆", "排行榜", "看看谁是最佳读者"),
        ("📝", "书评广场", "分享读书感悟"),
        ("🛍️", "装扮商店", "用积分装扮你的宠物"),
        ("🎯", "阅读挑战", "完成挑战赢取大量积分"),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <span class="icon">{icon}</span>
                <div class="title">{title}</div>
                <div class="desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")  # spacing

else:
    # ── 未登录：居中登录卡片 ──
    col_l, col_c, col_r = st.columns([1, 1.5, 1])
    with col_c:
        st.markdown("""
        <div class="login-header">
            <span class="pet-icon">📚</span>
            <h1>悦读养成记</h1>
            <div class="subtitle">阅读积分养宠物 — 让阅读成为习惯</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 登录", "📝 注册"])

        with tab_login:
            with st.form("login_form"):
                sid = st.text_input("学号", placeholder="请输入学号")
                pwd = st.text_input("密码", type="password", placeholder="初始密码为身份证后八位（X用0代替）")
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
                r_idcard = st.text_input("身份证号", placeholder="请输入身份证号（末位X将自动转为0）", type="password")
                st.caption("密码将自动设置为身份证后八位（X→0）")
                r_submit = st.form_submit_button("注册", use_container_width=True)
                if r_submit:
                    ok, msg = register(r_sid, r_name, r_college, r_major, r_idcard)
                    if ok:
                        st.success(msg + " 请切换到登录标签页登录。")
                    else:
                        st.error(msg)
