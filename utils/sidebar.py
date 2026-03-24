"""侧边栏公共组件：退出登录 + 隐藏管理后台 + 全局移动端适配样式"""
import streamlit as st

MOBILE_CSS = """
<style>
/* ===== 引入思源黑体（Noto Sans SC） ===== */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

/* 全局中文字体 */
html, body, [class*="st-"], .stMarkdown, .stButton > button,
.stTextInput input, .stSelectbox select, .stTextArea textarea,
[data-testid="stMetric"], [data-testid="stMetricValue"] {
    font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ===== 全局移动端适配 ===== */

/* 移动端收起侧边栏 */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { min-width: 0 !important; }
    [data-testid="stSidebar"][aria-expanded="true"] { min-width: 260px !important; }
}

/* 主内容区域移动端内边距 */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.8rem !important;
        max-width: 100% !important;
    }
    /* 标题缩小 */
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.1rem !important; }
}

/* 按钮触摸优化 */
.stButton > button {
    min-height: 44px;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease;
}
.stButton > button:active {
    transform: scale(0.97);
}

/* 输入框触摸优化 */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    min-height: 44px !important;
    font-size: 16px !important;  /* 防止 iOS 自动放大 */
    border-radius: 10px !important;
}

/* Tab 标签优化 */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    min-height: 44px;
    padding: 0.5rem 1rem;
    font-size: 0.95rem !important;
}

/* metric 卡片美化 */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 12px;
    padding: 0.8rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-testid="stMetric"] label {
    font-size: 0.85rem !important;
    color: #666 !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #333 !important;
}
@media (max-width: 768px) {
    [data-testid="stMetric"] {
        padding: 0.5rem 0.4rem;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
}

/* expander 圆角 */
.streamlit-expanderHeader {
    border-radius: 10px !important;
    font-size: 0.95rem !important;
}

/* 进度条圆角 */
.stProgress > div > div {
    border-radius: 10px !important;
}

/* st.container border 圆角 */
[data-testid="stVerticalBlock"] > div[data-testid="stExpander"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
}

/* 移动端多列自动换行 */
@media (max-width: 640px) {
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        min-width: 48% !important;
        flex: 1 1 48% !important;
    }
}

/* 极小屏幕单列 */
@media (max-width: 400px) {
    [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }
}

/* alert/info/warning 圆角 */
.stAlert {
    border-radius: 10px !important;
}

/* form 容器 */
[data-testid="stForm"] {
    border-radius: 12px !important;
    border: 1px solid #e0e0e0 !important;
    padding: 1rem !important;
}

/* 侧边栏美化 */
[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    font-size: 0.9rem;
}
</style>
"""


def setup_sidebar():
    """在每个页面调用，注入全局样式 + 设置侧边栏退出按钮 + 隐藏管理后台"""
    # 注入全局移动端适配样式
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

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
