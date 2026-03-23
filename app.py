"""悦读养成记 — 入口：登录 / 注册"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.auth import login, register
from utils.sidebar import setup_sidebar

st.set_page_config(
    page_title="悦读养成记",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 自定义样式（含移动端适配） ──
st.markdown("""
<style>
/* 登录页背景 */
[data-testid="stMain"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}
/* 登录头部 */
.login-header {
    text-align: center;
    margin-bottom: 1.2rem;
    padding-top: 1rem;
}
.login-header .pet-icon {
    font-size: 3.5rem;
    display: block;
    margin-bottom: 0.3rem;
}
.login-header h1 {
    font-size: 2rem;
    margin: 0;
    color: #333;
}
.login-header .subtitle {
    color: #888;
    font-size: 0.95rem;
    margin-top: 0.3rem;
}
/* 功能卡片 */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}
@media (max-width: 768px) {
    .feature-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.6rem;
    }
}
@media (max-width: 400px) {
    .feature-grid {
        grid-template-columns: 1fr;
    }
}
.feature-card {
    background: white;
    border-radius: 16px;
    padding: 1.2rem 0.8rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
}
.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}
.feature-card .icon {
    font-size: 2.2rem;
    display: block;
    margin-bottom: 0.3rem;
}
.feature-card .title {
    font-weight: 700;
    font-size: 1rem;
    color: #333;
}
.feature-card .desc {
    color: #888;
    font-size: 0.8rem;
    margin-top: 0.2rem;
}
/* 欢迎横幅 */
.welcome-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 1.5rem 1rem;
    color: white;
    text-align: center;
    margin-bottom: 1.2rem;
}
.welcome-banner h2 {
    margin: 0;
    font-size: 1.5rem;
}
.welcome-banner p {
    margin: 0.4rem 0 0 0;
    opacity: 0.9;
    font-size: 0.9rem;
}
@media (max-width: 768px) {
    .login-header h1 { font-size: 1.6rem; }
    .login-header .pet-icon { font-size: 3rem; }
    .welcome-banner { padding: 1rem 0.8rem; }
    .welcome-banner h2 { font-size: 1.3rem; }
}
/* 输入框 iOS 防缩放 */
input, textarea, select { font-size: 16px !important; }
/* 按钮 */
.stButton > button {
    min-height: 44px;
    border-radius: 10px !important;
}
/* Form 圆角 */
[data-testid="stForm"] {
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ── session 初始化 ──
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_id = ""
    st.session_state.user_name = ""
    st.session_state.is_admin = False


# ── 已登录 ──
if st.session_state.logged_in:
    setup_sidebar()

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
    cards_html = '<div class="feature-grid">'
    for icon, title, desc in features:
        cards_html += f"""
        <div class="feature-card">
            <span class="icon">{icon}</span>
            <div class="title">{title}</div>
            <div class="desc">{desc}</div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

else:
    # ── 未登录：居中登录卡片 ──
    col_l, col_c, col_r = st.columns([0.5, 2, 0.5])
    with col_c:
        st.markdown("""
        <div class="login-header">
            <span class="pet-icon">📚</span>
            <h1>悦读养成记</h1>
            <div class="subtitle">阅读积分养宠物 — 让阅读成为习惯</div>
        </div>
        """, unsafe_allow_html=True)

        # 注册成功后显示提示
        if st.session_state.get("show_login"):
            st.success("注册成功！请登录。")
            st.session_state.show_login = False

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
                        st.success(msg + " 即将跳转到登录...")
                        st.session_state.show_login = True
                        import time
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(msg)
