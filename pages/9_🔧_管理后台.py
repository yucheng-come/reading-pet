"""管理后台页面"""
import streamlit as st
import sys, os, uuid, csv, io
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.sidebar import setup_sidebar

from utils.auth import is_admin, get_user, batch_import_users, reset_password_by_idcard, id_card_to_password, _hash_password
from utils.data_io import read_json, write_json
from utils.points_engine import get_balance, earn_points
from utils.time_utils import now_str, this_month_str, today_str

st.set_page_config(page_title="管理后台", page_icon="🔧")

setup_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()

sid = st.session_state.student_id
if not is_admin(sid):
    st.error("仅管理员可访问此页面")
    st.stop()

st.title("🔧 管理后台")

tab_users, tab_import, tab_borrow, tab_reviews, tab_challenges, tab_stats = st.tabs(
    ["👤 用户管理", "📥 账号导入", "📚 借阅导入", "📝 书评审核", "🎯 挑战管理", "📊 数据统计"]
)

# ── 用户管理 ──
with tab_users:
    st.subheader("用户列表")
    users = read_json("users.json")

    # 添加单个账号
    st.markdown("#### 添加账号")
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            a_sid = st.text_input("学号", placeholder="请输入学号")
            a_name = st.text_input("姓名", placeholder="请输入姓名")
            a_idcard = st.text_input("身份证号", placeholder="请输入身份证号")
        with col2:
            a_college = st.text_input("学院", placeholder="请输入学院")
            a_major = st.text_input("专业", placeholder="请输入专业")
            st.caption("密码自动设为身份证后八位（X→0）")
        if st.form_submit_button("添加账号", use_container_width=True):
            if not all([a_sid, a_name, a_college, a_major, a_idcard]):
                st.error("所有字段均为必填")
            elif a_sid in users:
                st.error("该学号已存在")
            elif len(a_idcard) < 8:
                st.error("身份证号长度不正确")
            else:
                pwd = id_card_to_password(a_idcard)
                users[a_sid] = {
                    "student_id": a_sid,
                    "name": a_name,
                    "college": a_college,
                    "major": a_major,
                    "id_card_last8": pwd,
                    "password": _hash_password(pwd, a_sid),
                    "is_admin": False,
                }
                write_json("users.json", users)
                st.toast(f"账号 {a_sid} 添加成功！密码为身份证后八位")
                st.rerun()

    st.divider()

    # 搜索与列表
    search = st.text_input("搜索用户（学号或姓名）", key="user_search")
    user_list = []
    for uid, u in users.items():
        if u.get("is_admin"):
            continue
        if search and search not in uid and search not in u.get("name", ""):
            continue
        user_list.append(u)

    st.caption(f"共 {len(user_list)} 个用户")

    # 一次性计算所有用户余额，避免 N+1 查询
    all_logs = read_json("points_log.json")
    balance_map = {}
    for l in all_logs:
        balance_map[l["student_id"]] = balance_map.get(l["student_id"], 0) + l["amount"]

    for u in user_list:
        bal = balance_map.get(u["student_id"], 0)
        with st.expander(f"{u['name']} ({u['student_id']}) — {u['college']} — 积分: {bal}"):
            st.markdown(f"**学号**: {u['student_id']}")
            st.markdown(f"**姓名**: {u['name']}")
            st.markdown(f"**学院**: {u['college']}")
            st.markdown(f"**专业**: {u['major']}")
            st.markdown(f"**积分**: {bal}")
            # 重置密码
            reset_idcard = st.text_input("输入身份证号重置密码", key=f"idcard_{u['student_id']}", placeholder="输入该用户身份证号")
            if st.button("重置密码为身份证后八位", key=f"reset_{u['student_id']}"):
                if not reset_idcard or len(reset_idcard) < 8:
                    st.error("请输入有效的身份证号")
                else:
                    ok, msg = reset_password_by_idcard(u['student_id'], reset_idcard)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

# ── 账号导入与对比 ──
with tab_import:
    st.subheader("📥 账号信息库导入与对比")
    st.markdown("""
    上传 CSV 文件，格式要求（含表头）：

    | student_id | name | college | major | id_card |
    |------------|------|---------|-------|---------|
    | 2024001 | 张三 | 计算机学院 | 软件工程 | 110101200001011234 |

    - 密码自动设置为身份证后八位（末位X自动转为0）
    - 已存在的学号将跳过，不会覆盖
    """)

    uploaded = st.file_uploader("选择 CSV 文件", type=["csv"])
    if uploaded:
        try:
            content = uploaded.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))
            records = list(reader)
        except Exception as e:
            st.error(f"文件读取失败: {e}")
            records = []

        if records:
            st.markdown(f"**读取到 {len(records)} 条记录**")

            # 对比分析
            users = read_json("users.json")
            new_records = []
            existing_records = []
            invalid_records = []
            for r in records:
                s = str(r.get("student_id", "")).strip()
                if not s or not r.get("name", "").strip():
                    invalid_records.append(r)
                elif s in users:
                    existing_records.append(r)
                else:
                    new_records.append(r)

            col1, col2, col3 = st.columns(3)
            col1.metric("新增账号", len(new_records), delta=None)
            col2.metric("已存在（跳过）", len(existing_records))
            col3.metric("信息不全", len(invalid_records))

            # 预览新增
            if new_records:
                st.markdown("#### 即将新增的账号")
                preview_data = []
                for r in new_records[:20]:
                    preview_data.append({
                        "学号": r.get("student_id", ""),
                        "姓名": r.get("name", ""),
                        "学院": r.get("college", ""),
                        "专业": r.get("major", ""),
                    })
                st.dataframe(preview_data, use_container_width=True)
                if len(new_records) > 20:
                    st.caption(f"... 还有 {len(new_records) - 20} 条未显示")

            # 预览已存在
            if existing_records:
                with st.expander(f"查看已存在的 {len(existing_records)} 个账号"):
                    for r in existing_records:
                        s = str(r.get("student_id", "")).strip()
                        u = users.get(s, {})
                        file_name = str(r.get("name", "")).strip()
                        db_name = u.get("name", "")
                        match = "✅" if file_name == db_name else f"⚠️ 库中为「{db_name}」"
                        st.markdown(f"- {s} {file_name} {match}")

            # 预览无效
            if invalid_records:
                with st.expander(f"查看信息不全的 {len(invalid_records)} 条"):
                    for r in invalid_records:
                        st.markdown(f"- {r}")

            # 执行导入
            if new_records:
                if st.button(f"确认导入 {len(new_records)} 个新账号", use_container_width=True, type="primary"):
                    success, skipped, errors = batch_import_users(new_records)
                    st.toast(f"导入完成！成功 {success} 个，跳过 {skipped} 个")
                    if errors:
                        for e in errors:
                            st.warning(e)
                    st.rerun()
            elif not invalid_records:
                st.info("所有账号均已存在，无需导入")

# ── 借阅记录导入 ──
with tab_borrow:
    st.subheader("📚 借阅记录批量导入")
    st.markdown("""
    从学习通或图书馆系统导出借阅记录 CSV，上传后自动为学生发放积分。

    **CSV 格式要求（含表头）：**

    | student_id | book | action | date |
    |------------|------|--------|------|
    | 2024001 | 红楼梦 | borrow | 2026-03-20 |
    | 2024001 | 三体 | return | 2026-03-21 |

    - **action**: `borrow`（借阅，+10积分）或 `return`（归还，+5积分）
    - **date**: 借还日期（YYYY-MM-DD），留空则默认今天
    - 系统会自动去重，同一学号同一天同一本书同一操作不会重复计分
    """)

    borrow_file = st.file_uploader("选择借阅记录 CSV", type=["csv"], key="borrow_csv")
    if borrow_file:
        try:
            b_content = borrow_file.read().decode("utf-8-sig")
            b_reader = csv.DictReader(io.StringIO(b_content))
            b_records = list(b_reader)
        except Exception as e:
            st.error(f"文件读取失败: {e}")
            b_records = []

        if b_records:
            st.markdown(f"**读取到 {len(b_records)} 条记录**")

            # 预处理和分类
            users = read_json("users.json")
            existing_logs = read_json("points_log.json")

            # 构建已有记录指纹集合（用于去重）
            existing_fingerprints = set()
            for l in existing_logs:
                if l["action"] in ("borrow", "return"):
                    # 指纹 = 学号+操作+日期+书名关键词
                    note = l.get("note", "")
                    fp = f"{l['student_id']}|{l['action']}|{l['time'][:10]}|{note}"
                    existing_fingerprints.add(fp)

            valid_records = []
            unknown_students = []
            invalid_records = []
            duplicate_records = []

            for r in b_records:
                r_sid = str(r.get("student_id", "")).strip()
                r_book = str(r.get("book", "")).strip()
                r_action = str(r.get("action", "")).strip().lower()
                r_date = str(r.get("date", "")).strip() or today_str()

                # 验证字段
                if not r_sid or not r_book:
                    invalid_records.append(r)
                    continue
                if r_action not in ("borrow", "return"):
                    invalid_records.append(r)
                    continue

                # 检查学号是否存在
                if r_sid not in users:
                    unknown_students.append(r)
                    continue

                # 去重检查
                action_label = "借阅" if r_action == "borrow" else "归还"
                note = f"{action_label}《{r_book}》"
                fp = f"{r_sid}|{r_action}|{r_date}|{note}"
                if fp in existing_fingerprints:
                    duplicate_records.append(r)
                    continue

                existing_fingerprints.add(fp)
                valid_records.append({
                    "student_id": r_sid,
                    "book": r_book,
                    "action": r_action,
                    "date": r_date,
                    "note": note,
                    "name": users[r_sid].get("name", ""),
                })

            # 统计概览
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("可导入", len(valid_records))
            col2.metric("已存在（跳过）", len(duplicate_records))
            col3.metric("学号不存在", len(unknown_students))
            col4.metric("格式错误", len(invalid_records))

            # 积分预估
            if valid_records:
                from config import POINTS_RULES
                borrow_pts = POINTS_RULES["borrow"]["points"]
                return_pts = POINTS_RULES["return"]["points"]
                est_borrow = sum(1 for r in valid_records if r["action"] == "borrow")
                est_return = sum(1 for r in valid_records if r["action"] == "return")
                total_est = est_borrow * borrow_pts + est_return * return_pts
                st.info(f"预计发放积分: 借阅 {est_borrow} 次(+{est_borrow * borrow_pts}) + 归还 {est_return} 次(+{est_return * return_pts}) = **{total_est} 积分**")

                # 预览列表
                st.markdown("#### 即将导入的记录")
                preview = []
                for r in valid_records[:30]:
                    action_cn = "📗 借阅" if r["action"] == "borrow" else "📕 归还"
                    pts = borrow_pts if r["action"] == "borrow" else return_pts
                    preview.append({
                        "学号": r["student_id"],
                        "姓名": r["name"],
                        "书名": r["book"],
                        "操作": action_cn,
                        "日期": r["date"],
                        "积分": f"+{pts}",
                    })
                st.dataframe(preview, use_container_width=True)
                if len(valid_records) > 30:
                    st.caption(f"... 还有 {len(valid_records) - 30} 条未显示")

                # 执行导入
                if st.button(f"确认导入 {len(valid_records)} 条借阅记录", use_container_width=True, type="primary"):
                    success_count = 0
                    fail_count = 0
                    for r in valid_records:
                        ok, msg, pts = earn_points(r["student_id"], r["action"], r["note"])
                        if ok:
                            success_count += 1
                        else:
                            fail_count += 1
                    result_msg = f"导入完成！成功 {success_count} 条"
                    if fail_count > 0:
                        result_msg += f"，{fail_count} 条因当日上限跳过"
                    st.toast(result_msg)
                    st.rerun()

            # 显示问题记录
            if unknown_students:
                with st.expander(f"查看学号不存在的 {len(unknown_students)} 条"):
                    for r in unknown_students:
                        st.markdown(f"- {r.get('student_id', '')} 《{r.get('book', '')}》")

            if invalid_records:
                with st.expander(f"查看格式错误的 {len(invalid_records)} 条"):
                    for r in invalid_records:
                        st.markdown(f"- {r}")

            if duplicate_records:
                with st.expander(f"查看已存在的 {len(duplicate_records)} 条"):
                    for r in duplicate_records:
                        st.markdown(f"- {r.get('student_id', '')} 《{r.get('book', '')}》 {r.get('action', '')} {r.get('date', '')}")

# ── 书评审核 ──
with tab_reviews:
    st.subheader("待审核书评")
    reviews = read_json("reviews.json")
    pending = [r for r in reviews if r.get("type") == "review" and r.get("status") == "pending"]

    if not pending:
        st.success("暂无待审核书评")
    else:
        st.caption(f"共 {len(pending)} 篇待审核")
        for r in pending:
            with st.expander(f"《{r['book']}》— {r.get('author_name', '匿名')} ({r.get('time', '')})"):
                st.markdown(f"**作者**: {r.get('book_author', '')}")
                st.markdown(f"**评分**: {'⭐' * r.get('rating', 0)}")
                st.markdown(f"**字数**: {len(r.get('content', ''))}")
                st.markdown(r.get("content", ""))
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 通过", key=f"approve_{r['id']}", use_container_width=True):
                        for rev in reviews:
                            if rev.get("id") == r["id"]:
                                rev["status"] = "approved"
                                break
                        write_json("reviews.json", reviews)
                        # 审核通过后发放书评积分
                        earn_points(r["student_id"], "review", f"书评《{r['book']}》审核通过")
                        st.toast("已通过，积分已发放")
                        st.rerun()
                with col2:
                    if st.button("❌ 拒绝", key=f"reject_{r['id']}", use_container_width=True):
                        for rev in reviews:
                            if rev.get("id") == r["id"]:
                                rev["status"] = "rejected"
                                break
                        write_json("reviews.json", reviews)
                        st.toast("已拒绝")
                        st.rerun()

    st.divider()
    st.subheader("全部书评")
    status_filter = st.selectbox("状态筛选", ["全部", "待审核", "已通过", "已拒绝"])
    all_reviews = [r for r in reviews if r.get("type") == "review"]
    if status_filter == "待审核":
        all_reviews = [r for r in all_reviews if r.get("status") == "pending"]
    elif status_filter == "已通过":
        all_reviews = [r for r in all_reviews if r.get("status") == "approved"]
    elif status_filter == "已拒绝":
        all_reviews = [r for r in all_reviews if r.get("status") == "rejected"]

    st.caption(f"共 {len(all_reviews)} 篇")
    for r in all_reviews:
        status_map = {"pending": "🔵 待审核", "approved": "✅ 已通过", "rejected": "❌ 已拒绝"}
        st.markdown(f"- 《{r['book']}》— {r.get('author_name', '')} | {status_map.get(r.get('status'), '')} | 👍{r.get('votes', 0)}")

# ── 挑战管理 ──
with tab_challenges:
    st.subheader("管理阅读挑战")
    challenges = read_json("challenges.json")
    if not isinstance(challenges, list):
        challenges = []

    st.markdown("#### 创建新挑战")
    with st.form("new_challenge"):
        c_title = st.text_input("挑战标题")
        c_desc = st.text_area("挑战描述")
        c_type = st.selectbox("类型", ["borrow", "review", "checkin_streak", "recommend"])
        c_target = st.number_input("目标数量", min_value=1, value=3)
        c_reward = st.number_input("奖励积分", min_value=10, value=50, step=10)
        c_month = st.text_input("所属月份", value=this_month_str())
        if st.form_submit_button("创建挑战", use_container_width=True):
            if not c_title.strip():
                st.error("请输入标题")
            else:
                new_ch = {
                    "id": str(uuid.uuid4())[:8],
                    "title": c_title.strip(),
                    "description": c_desc.strip(),
                    "target": c_target,
                    "type": c_type,
                    "reward": c_reward,
                    "month": c_month,
                    "participants": {},
                }
                challenges.append(new_ch)
                write_json("challenges.json", challenges)
                st.toast("挑战创建成功！")
                st.rerun()

    st.divider()
    st.markdown("#### 现有挑战")
    for ch in challenges:
        participants = ch.get("participants", {})
        completed = sum(1 for p in participants.values() if p.get("completed"))
        with st.expander(f"{ch['title']} ({ch.get('month', '')}) — 参与: {len(participants)} | 完成: {completed}"):
            st.markdown(f"**描述**: {ch['description']}")
            st.markdown(f"**类型**: {ch['type']} | **目标**: {ch['target']} | **奖励**: {ch['reward']}分")
            if st.button("删除挑战", key=f"del_ch_{ch['id']}"):
                challenges = [c for c in challenges if c["id"] != ch["id"]]
                write_json("challenges.json", challenges)
                st.rerun()

# ── 数据统计 ──
with tab_stats:
    st.subheader("📊 数据统计")
    users = read_json("users.json")
    logs = read_json("points_log.json")
    reviews = read_json("reviews.json")

    user_count = sum(1 for u in users.values() if not u.get("is_admin"))
    total_points = sum(l["amount"] for l in logs if l["amount"] > 0)
    review_count = sum(1 for r in reviews if r.get("type") == "review")
    month = this_month_str()
    month_active = len(set(l["student_id"] for l in logs if l["time"][:7] == month))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("注册用户", user_count)
    col2.metric("本月活跃", month_active)
    col3.metric("总发放积分", total_points)
    col4.metric("书评总数", review_count)

    st.divider()

    st.markdown("#### 近7天积分发放")
    from datetime import date, timedelta
    daily_points = {}
    for i in range(6, -1, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        daily_points[d] = sum(l["amount"] for l in logs if l["time"][:10] == d and l["amount"] > 0)

    for d, pts in daily_points.items():
        bar = "█" * (pts // 10) if pts > 0 else "—"
        st.markdown(f"`{d}` {bar} **{pts}**")

    st.divider()

    st.markdown("#### 学院用户分布")
    college_counts = {}
    for u in users.values():
        if u.get("is_admin"):
            continue
        college = u.get("college", "未知")
        college_counts[college] = college_counts.get(college, 0) + 1

    for college, count in sorted(college_counts.items(), key=lambda x: x[1], reverse=True):
        st.markdown(f"- **{college}**: {count} 人")
