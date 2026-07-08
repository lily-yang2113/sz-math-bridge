# -*- coding: utf-8 -*-
"""
苏州初一数学暑假衔接 - AI全自动私教系统
Streamlit App - 无需家长干预，孩子自主学习
"""

import streamlit as st
import json
import os
import datetime
from pathlib import Path
from content import CHAPTERS, SECTION_LIST, SECTIONS, get_section_ids
from collections import defaultdict
import socket
from cat_manager import get_cat_styles, get_cat_html, init_cat_session
from cat_manager import on_correct_answer, on_wrong_answer, on_all_done
from cat_manager import update_cat_mood, clear_cat_action, CatMood

# ============================================================
# 配置页面
# ============================================================
st.set_page_config(
    page_title="小升初数学衔接 · 苏州版",
    page_icon="\U0001F4D0",
    layout="wide",
)

# ============================================================
# 自定义CSS - 大字体、柔和配色、适合儿童
# ============================================================
st.markdown("""
<style>
    .stApp { background: #f0f7f4; }
    .main > div { padding: 1rem 2rem; }
    h1, h2, h3 { color: #2d6a4f; }
    .stButton button {
        font-size: 1.2rem !important; padding: 0.5rem 1.5rem;
        border-radius: 12px; background: #52b788; color: white; border: none;
        font-weight: 600;
    }
    .stButton button:hover { background: #40916c; }
    .lesson-card {
        background: #fff; border-radius: 16px; padding: 1.5rem 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem;
    }
    .example-card {
        background: #e8f5e9; border-radius: 12px; padding: 1.2rem 1.5rem;
        border-left: 5px solid #2d6a4f; margin-bottom: 0.8rem;
    }
    .hint-card {
        background: #fff3cd; border-radius: 8px; padding: 0.8rem 1.2rem;
        border-left: 4px solid #ffc107; margin: 0.5rem 0;
    }
    .correct-feedback { background: #d4edda; border-radius: 10px; padding: 0.8rem 1.2rem; color: #155724; font-weight: 600; }
    .wrong-feedback { background: #f8d7da; border-radius: 10px; padding: 0.8rem 1.2rem; color: #721c24; font-weight: 600; }
    .stProgress > div > div { background: #52b788; }
    .stTabs [data-baseweb="tab"] { font-size: 1.2rem !important; padding: 0.6rem 1.2rem; font-weight: 600; }
    section[data-testid="stSidebar"] { background: #e8f5e9; }
    section[data-testid="stSidebar"] .stMarkdown { font-size: 1rem; }
    .badge { display: inline-block; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.9rem; font-weight: 600; margin-right: 0.5rem; }
    .badge-done { background: #d4edda; color: #155724; }
    .badge-pending { background: #f8f9fa; color: #666; }
</style>
""", unsafe_allow_html=True)

st.markdown(get_cat_styles(), unsafe_allow_html=True)

# ============================================================
# 数据文件路径
# ============================================================
DATA_DIR = Path(__file__).parent / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"
WRONG_FILE = DATA_DIR / "wrong_questions.json"
DAILY_FILE = DATA_DIR / "daily_report.txt"

for d in [DATA_DIR]:
    d.mkdir(exist_ok=True)


# ============================================================
# 数据读写函数
# ============================================================
def load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_session_state():
    """初始化 session state"""
    if "progress" not in st.session_state:
        st.session_state.progress = load_json(PROGRESS_FILE, {})
    if "wrong_questions" not in st.session_state:
        st.session_state.wrong_questions = load_json(WRONG_FILE, [])
    if "current_section" not in st.session_state:
        st.session_state.current_section = SECTION_LIST[0][0]
    if "study_timer_start" not in st.session_state:
        st.session_state.study_timer_start = datetime.datetime.now()
    if "hint_count" not in st.session_state:
        st.session_state.hint_count = {}
    if "q_answers" not in st.session_state:
        st.session_state.q_answers = {}
    if "q_feedback" not in st.session_state:
        st.session_state.q_feedback = {}
    if "t_answers" not in st.session_state:
        st.session_state.t_answers = {}
    if "t_feedback" not in st.session_state:
        st.session_state.t_feedback = {}
    if "test_submitted" not in st.session_state:
        st.session_state.test_submitted = False
    if "practicing" not in st.session_state:
        st.session_state.practicing = False
    if "testing" not in st.session_state:
        st.session_state.testing = False
        init_cat_session()
        if "cat_mood_mgr" not in st.session_state:
            st.session_state.cat_mood_mgr = CatMood(DATA_DIR)


# ============================================================
# 学习进度保存
# ============================================================
def save_progress(section_id, test_score, total_test):
    today = datetime.date.today().isoformat()
    if section_id not in st.session_state.progress:
        st.session_state.progress[section_id] = {"scores": [], "dates": []}
    st.session_state.progress[section_id]["scores"].append(test_score)
    st.session_state.progress[section_id]["dates"].append(today)
    save_json(PROGRESS_FILE, st.session_state.progress)


def save_wrong(q_data):
    entry = {
        "section": st.session_state.current_section,
        "question": q_data["q"],
        "knowledge_point": q_data.get("knowledge_point", ""),
        "date": datetime.date.today().isoformat(),
    }
    st.session_state.wrong_questions.append(entry)
    save_json(WRONG_FILE, st.session_state.wrong_questions)


# ============================================================
# 检查答案（支持多种题型）
# ============================================================
def check_answer(user_input, correct_answer, qtype):
    if user_input is None or user_input.strip() == "":
        return False
    user = user_input.strip()
    correct = str(correct_answer).strip()
    if qtype == "numeric":
        try:
            return abs(float(user) - float(correct)) < 0.001
        except:
            return user == correct
    elif qtype == "choice":
        return user == correct
    else:
        return user.replace(" ", "") == correct.replace(" ", "")


# ============================================================
# 侧边栏
# ============================================================

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def render_sidebar():
    with st.sidebar:
        st.markdown("### \U0001F9EE 小升初数学衔接")
        st.markdown("**苏科版 · 苏州专用**")
        st.divider()
        st.divider()
        local_ip = get_local_ip()
        st.markdown(
            "<div style='background:#fff;border-radius:12px;padding:0.8rem 1rem;margin-bottom:0.5rem;border:2px solid #52b788;'>"
            "<span style='color:#2d6a4f;font-weight:600;font-size:1rem;'>平板/手机访问</span><br>"
            f"<span style='font-size:0.95rem;color:#333;'>同一WiFi下，在平板浏览器输入：</span><br>"
            f"<span style='font-size:1.3rem;font-weight:700;color:#1b4332;'>{local_ip}:8501</span></div>",
            unsafe_allow_html=True,
        )

        progress = st.session_state.progress
        total = len(SECTION_LIST)
        done = len([s for s in get_section_ids() if s in progress and progress[s].get("scores", [])])
        pct = done / total if total > 0 else 0
        st.markdown(f"**学习进度**: {done}/{total} 节")
        st.progress(pct)

        if done > 0:
            scores_list = [max(progress[s]["scores"]) for s in progress if progress[s].get("scores")]
            if scores_list:
                avg_score = sum(scores_list) / len(scores_list)
                st.markdown(f"**平均得分**: {avg_score:.0f}/100")

        st.divider()
        st.markdown("### \U0001F4D6 选择章节")

        current_sec = st.session_state.current_section

        for ch_num, ch_title, sections in CHAPTERS:
            st.markdown(f"**{ch_num} {ch_title}**")
            for sec_id, sec_title in sections:
                status = ""
                if sec_id in progress and progress[sec_id].get("scores"):
                    status = " \u2705"

                label = f"{sec_id} {sec_title}{status}"
                if st.button(label, key=f"sec_{sec_id}", use_container_width=True):
                    st.session_state.current_section = sec_id
                    st.session_state.hint_count = {}
                    st.session_state.q_answers = {}
                    st.session_state.q_feedback = {}
                    st.session_state.t_answers = {}
                    st.session_state.t_feedback = {}
                    st.session_state.test_submitted = False
                    st.session_state.practicing = False
                    st.session_state.testing = False
                    st.rerun()

        st.divider()

        wrong_count = len(st.session_state.wrong_questions)
        if wrong_count > 0:
            st.markdown(f"\U0001F4DD 错题本: **{wrong_count}** 道题")
        else:
            st.markdown("\U0001F4DD 错题本: 暂无错题")

        elapsed = datetime.datetime.now() - st.session_state.study_timer_start
        mins = int(elapsed.total_seconds() / 60)
        st.markdown(f"\u23F1\uFE0F 本次学习: **{mins}** 分钟")

        st.divider()
        st.markdown(
            "**\U0001F4A1 每节课流程：**\n\n"
            "\U0001F4D6 阅读讲解 \u2192 \U0001F4DD 看例题 \u2192 \u270F\uFE0F 做练习 \u2192 \u2705 闯关测试"
        )


# ============================================================
# 主页 - 显示当前章节的学习内容
# ============================================================
def render_main():
    sec_id = st.session_state.current_section
    elapsed = datetime.datetime.now() - st.session_state.study_timer_start
    mins = int(elapsed.total_seconds() / 60)

    info = None
    for sid, ch_label, sec_title in SECTION_LIST:
        if sid == sec_id:
            info = (sid, ch_label, sec_title)
            break

    if info is None:
        st.error("章节未找到")
        return

    sid, ch_label, sec_title = info
    content = SECTIONS.get(sid)
    if content is None:
        st.error("内容未加载")
        return

    st.markdown(f"## \U0001F4DA {sid} {sec_title}")
    st.markdown(f"<small>{ch_label}</small>", unsafe_allow_html=True)

    is_done = sid in st.session_state.progress and st.session_state.progress[sid].get("scores")

    tabs = st.tabs(["\U0001F4D6 学新知", "\U0001F4DD 看例题", "\u270F\uFE0F 做练习", "\u2705 闯关测试"])

    # ======================== TAB 1: 讲授 ========================
    with tabs[0]:
        st.markdown('<div class="lesson-card">', unsafe_allow_html=True)
        st.markdown(content["lesson"])
        st.markdown('</div>', unsafe_allow_html=True)

    # ======================== TAB 2: 例题 ========================
    with tabs[1]:
        for i, ex in enumerate(content["examples"], 1):
            st.markdown(f'<div class="example-card">', unsafe_allow_html=True)
            st.markdown(f"### {ex['title']}")
            st.markdown(f"**题目**：{ex['question']}")
            st.markdown("**解题步骤**：")
            for j, step in enumerate(ex["steps"], 1):
                st.markdown(f"{j}. {step}")
            st.markdown(f"**答案**：{ex['answer']}")
            st.markdown('</div>', unsafe_allow_html=True)
            if i < len(content["examples"]):
                st.markdown("---")

    # ======================== TAB 3: 练习 ========================
    with tabs[2]:
        gen_practice = content["practice"]
        questions = gen_practice()

        if not st.session_state.practicing:
            st.markdown("准备好开始练习了吗？每道题有 **3 次** 提示机会哦！")
            if st.button("\U0001F680 开始练习", key="start_practice"):
                st.session_state.practicing = True
                st.session_state.q_answers = {}
                st.session_state.q_feedback = {}
                st.session_state.hint_count = {}
                st.rerun()
        else:
            all_correct = True
            for i, q in enumerate(questions):
                qid = f"p_{i}"
                st.markdown(f'<div class="lesson-card">', unsafe_allow_html=True)
                st.markdown(f"**第 {i+1} 题**（{q.get('knowledge_point', '')}）")
                st.markdown(q["q"])

                if qid not in st.session_state.hint_count:
                    st.session_state.hint_count[qid] = 0

                if qid not in st.session_state.q_feedback:
                    if q["type"] == "choice":
                        opts = [o.split(". ", 1)[1] if ". " in o else o for o in q["options"]]
                        user_ans = st.radio("选择答案：", opts, key=f"q_{qid}", index=None)
                        if user_ans:
                            letter = chr(65 + opts.index(user_ans))
                            st.session_state.q_answers[qid] = letter
                    elif q["type"] == "numeric":
                        user_val = st.text_input("你的答案：", key=f"q_{qid}")
                        st.session_state.q_answers[qid] = user_val
                    else:
                        user_val = st.text_input("你的答案（不要加多余空格）：", key=f"q_{qid}")
                        st.session_state.q_answers[qid] = user_val

                    hint_col1, hint_col2 = st.columns([3, 1])
                    with hint_col2:
                        h_count = st.session_state.hint_count[qid]
                        if h_count < 3:
                            if st.button(f"\U0001F4A1 提示 ({3-h_count}/3)", key=f"hint_{qid}"):
                                st.session_state.hint_count[qid] += 1
                                st.rerun()

                    if h_count > 0:
                        with hint_col1:
                            hint_idx = min(h_count - 1, len(q["hints"]) - 1)
                            st.markdown(
                                f'<div class="hint-card">\U0001F4A1 提示：{q["hints"][hint_idx]}</div>',
                                unsafe_allow_html=True,
                            )

                    if st.button(f"\u270F\uFE0F 提交第 {i+1} 题", key=f"submit_{qid}"):
                        ans = st.session_state.q_answers.get(qid, "")
                        if ans:
                            correct = check_answer(ans, q["answer"], q["type"])
                            if correct:
                                st.session_state.q_feedback[qid] = "correct"
                                on_correct_answer()
                            else:
                                st.session_state.q_feedback[qid] = "wrong"
                                on_wrong_answer()
                                if st.session_state.hint_count.get(qid, 0) >= 3:
                                    st.session_state.q_feedback[qid] = "giveup"
                            st.rerun()
                        else:
                            st.warning("请先输入答案！")

                    if st.session_state.hint_count.get(qid, 0) >= 3 and qid not in st.session_state.q_feedback:
                        st.warning("\u26A0\uFE0F 提示次数已用完，请你认真思考后提交答案！")

                if qid in st.session_state.q_feedback:
                    fb = st.session_state.q_feedback[qid]
                    if fb == "correct":
                        st.markdown(
                            '<div class="correct-feedback">\u2705 回答正确！继续加油！</div>',
                            unsafe_allow_html=True,
                        )
                    elif fb == "wrong":
                        st.markdown(
                            f'<div class="wrong-feedback">\u274C 再想想哦！正确答案是：{q["answer"]}</div>',
                            unsafe_allow_html=True,
                        )
                        all_correct = False
                    elif fb == "giveup":
                        st.markdown(
                            f'<div class="wrong-feedback">\U0001F4D6 这道题的正确答案是：{q["answer"]}，记在错题本里啦！</div>',
                            unsafe_allow_html=True,
                        )
                        save_wrong(q)
                        all_correct = False

                st.markdown('</div>', unsafe_allow_html=True)

            all_done = all(qid in st.session_state.q_feedback for qid in [f"p_{i}" for i in range(len(questions))])
            if all_done:
                if all_correct:
                    st.balloons()
                    st.success("\U0001F389 太棒了！全部练习正确！可以进入闯关测试了！")
                else:
                    st.info("\U0001F4AA 有做错的题，错题已自动记录。可以先复习一下再去做测试哦！")
                if st.button("\U0001F504 重新练习", key="retry_practice"):
                    st.session_state.practicing = False
                    st.rerun()

    # ======================== TAB 4: 测试 ========================
    with tabs[3]:
        gen_test = content["test"]
        questions_test = gen_test()

        if is_done:
            last_score = max(st.session_state.progress[sid]["scores"])
            st.markdown(
                f'<div class="correct-feedback">\U0001F389 本章节已完成！最高分：{last_score}/100</div>',
                unsafe_allow_html=True,
            )
            if st.button("\U0001F504 重新测试", key="retest"):
                st.session_state.testing = False
                st.session_state.test_submitted = False
                st.session_state.t_answers = {}
                st.session_state.t_feedback = {}
                st.rerun()

        if not st.session_state.testing and not is_done:
            st.markdown("准备好了就去闯关测试吧！一共 3 道题。")
            if st.button("\U0001F3AF 开始测试", key="start_test"):
                st.session_state.testing = True
                st.session_state.test_submitted = False
                st.session_state.t_answers = {}
                st.session_state.t_feedback = {}
                st.rerun()

        if st.session_state.testing:
            test_answers = {}
            for i, q in enumerate(questions_test):
                qid = f"t_{i}"
                st.markdown(f'<div class="lesson-card">', unsafe_allow_html=True)
                st.markdown(f"**测试 {i+1}**（{q.get('knowledge_point', '')}）")
                st.markdown(q["q"])

                if not st.session_state.test_submitted:
                    if q["type"] == "choice":
                        opts = [o.split(". ", 1)[1] if ". " in o else o for o in q["options"]]
                        user_ans = st.radio("选择答案：", opts, key=f"t_{qid}", index=None)
                        if user_ans:
                            letter = chr(65 + opts.index(user_ans))
                            st.session_state.t_answers[qid] = letter
                    elif q["type"] == "numeric":
                        user_val = st.text_input("你的答案：", key=f"t_{qid}")
                        st.session_state.t_answers[qid] = user_val
                    else:
                        user_val = st.text_input("你的答案：", key=f"t_{qid}")
                        st.session_state.t_answers[qid] = user_val
                else:
                    fb = st.session_state.t_feedback.get(qid, {})
                    if fb.get("correct"):
                        st.markdown(
                            '<div class="correct-feedback">\u2705 正确！得 100 分</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<div class="wrong-feedback">\u274C 正确答案：{q["answer"]}</div>',
                            unsafe_allow_html=True,
                        )
                st.markdown('</div>', unsafe_allow_html=True)

            if not st.session_state.test_submitted:
                if st.button("\U0001F4CB 提交全部测试", key="submit_test"):
                    missing = [f"t_{i}" for i in range(len(questions_test)) if f"t_{i}" not in st.session_state.t_answers]
                    if missing:
                        st.warning(f"还有 {len(missing)} 道题没有回答，请完成后再提交！")
                    else:
                        score = 0
                        for i, q in enumerate(questions_test):
                            qid = f"t_{i}"
                            ans = st.session_state.t_answers.get(qid, "")
                            correct = check_answer(ans, q["answer"], q["type"])
                            st.session_state.t_feedback[qid] = {"correct": correct}
                            if correct:
                                score += 1
                            else:
                                save_wrong(q)

                        total = len(questions_test)
                        pct_score = int(score / total * 100)
                        save_progress(sid, pct_score, total)
                        st.session_state.test_submitted = True

                        if pct_score >= 80:
                            st.balloons()
                            st.success(f"\U0001F389 **测试完成！得分：{pct_score}/100**，太棒了！")
                        elif pct_score >= 60:
                            st.info(f"\U0001F4AA **测试完成！得分：{pct_score}/100**，及格了！可以复习后再来一次。")
                        else:
                            st.warning(f"\U0001F4D6 **测试完成！得分：{pct_score}/100**，错题已记录，建议重新学习后再测试。")

                        generate_daily_report()
                        st.rerun()

    if is_done:
        st.divider()
        with st.expander("\U0001F4CA 本日学习报告"):
            st.markdown(f"**日期**：{datetime.date.today().isoformat()}")
            st.markdown(f"**学习章节**：{sid} {sec_title}")
            st.markdown(f"**最高得分**：{max(st.session_state.progress[sid]['scores'])}/100")
            st.markdown(f"**学习时长**：{mins} 分钟")
            st.markdown("---")
            st.markdown("报告自动保存在 data/daily_report.txt")


# ============================================================
# 错题本页面
# ============================================================
def render_wrong_book():
    st.markdown("## \U0001F4DD 错题本")
    wrong = st.session_state.wrong_questions
    if not wrong:
        st.info("\U0001F389 目前还没有错题！继续保持！")
        return

    grouped = defaultdict(list)
    for w in wrong:
        grouped[w["section"]].append(w)

    for sec_id in sorted(grouped.keys()):
        info = next((s for s in SECTION_LIST if s[0] == sec_id), None)
        label = f"{sec_id} {info[2]}" if info else sec_id
        with st.expander(f"\U0001F4C2 {label}（{len(grouped[sec_id])} 题）"):
            for i, w in enumerate(grouped[sec_id], 1):
                st.markdown(f"{i}. {w['question']}")
                st.markdown(f"   *知识点：{w.get('knowledge_point', '未标注')}*")
                st.markdown(f"   *记录时间：{w['date']}*")

    if st.button("\U0001F5D1\uFE0F 清空错题本"):
        st.session_state.wrong_questions = []
        save_json(WRONG_FILE, [])
        st.rerun()


# ============================================================
# 进度总览页面
# ============================================================
def render_progress():
    st.markdown("## \U0001F4CA 学习进度总览")

    col1, col2, col3 = st.columns(3)
    total = len(SECTION_LIST)
    done = len([s for s in get_section_ids() if s in st.session_state.progress and st.session_state.progress[s].get("scores")])

    with col1:
        st.metric("已完成章节", f"{done}/{total}")
    with col2:
        if done > 0:
            scores_list = [max(st.session_state.progress[s]["scores"]) for s in st.session_state.progress if st.session_state.progress[s].get("scores")]
            avg = sum(scores_list) // len(scores_list)
            st.metric("平均分", f"{avg}/100")
        else:
            st.metric("平均分", "\u2014")
    with col3:
        st.metric("错题数", len(st.session_state.wrong_questions))

    st.divider()

    st.markdown("### 各章节成绩")
    for ch_num, ch_title, sections in CHAPTERS:
        st.markdown(f"**{ch_num} {ch_title}**")
        cols = st.columns(len(sections))
        for i, (sec_id, sec_title) in enumerate(sections):
            with cols[i]:
                if sec_id in st.session_state.progress and st.session_state.progress[sec_id].get("scores"):
                    s = max(st.session_state.progress[sec_id]["scores"])
                    if s >= 80:
                        st.markdown(f"{sec_id}<br><span style='color:#2d6a4f;font-size:1.5rem;'>\u2705</span> {s}分", unsafe_allow_html=True)
                    else:
                        st.markdown(f"{sec_id}<br><span style='color:#dc3545;font-size:1.5rem;'>\U0001F504</span> {s}分", unsafe_allow_html=True)
                else:
                    st.markdown(f"{sec_id}<br><span style='color:#ccc;font-size:1.5rem;'>\u2B1C</span> 未开始", unsafe_allow_html=True)
        st.markdown("")


# ============================================================
# 生成每日报告
# ============================================================
def generate_daily_report():
    today = datetime.date.today().isoformat()
    wrong_count = len(st.session_state.wrong_questions)

    done_today = []
    for s in st.session_state.progress:
        dates = st.session_state.progress[s].get("dates", [])
        if today in dates:
            info = next((x for x in SECTION_LIST if x[0] == s), None)
            if info:
                done_today.append(f"{s} {info[2]}")

    report = [
        "=" * 40,
        "\U0001F4CA 每日学习报告",
        f"日期：{today}",
        "=" * 40,
        f"今日学习章节：{', '.join(done_today) if done_today else '无'}",
        f"累计错题数：{wrong_count}",
        f"总进度：{len([s for s in get_section_ids() if s in st.session_state.progress])}/{len(SECTION_LIST)}",
        "",
        "\U0001F4A1 家长提示：如果今天没有学习记录或进度较慢，",
        "   可以和孩子聊聊学习感受哦！",
        "",
    ]

    with open(DAILY_FILE, "a", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n\n")


# ============================================================
# 首页欢迎
# ============================================================
def render_home():
    st.markdown("## \U0001F392 欢迎来到初中数学衔接课堂！")
    st.markdown(
        """
        <div class="lesson-card">
        <p style="font-size:1.3rem;">
        同学你好！\U0001F44B 欢迎来到苏州专属的初中数学预习课！
        </p>
        <p>
        这个暑假，我们一起来学 <b>苏科版七年级上册</b> 的数学内容。
        整个课程分为 <b>4 大章、16 节</b>，每一节都有：
        </p>
        <ul>
        <li>\U0001F4D6 <b>学新知</b> — 用苏州生活场景讲清楚知识点</li>
        <li>\U0001F4DD <b>看例题</b> — 跟着步骤学会解题方法</li>
        <li>\u270F\uFE0F <b>做练习</b> — 自己动手做，错了有提示</li>
        <li>\u2705 <b>闯关测试</b> — 测测你学会了多少！</li>
        </ul>
        <p style="font-size:1.1rem;color:#666;">
        \U0001F4A1 每道题有 <b>3 次提示机会</b>，大胆试试吧！
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### \U0001F4C5 今天建议学习")
    progress = st.session_state.progress
    for sec_id, ch_label, sec_title in SECTION_LIST:
        if sec_id not in progress or not progress[sec_id].get("scores"):
            st.info(f"\U0001F449 从 **{sec_id} {sec_title}** 开始吧！点击左侧菜单选择章节。")
            break
    else:
        st.success("\U0001F389 恭喜你！你已经完成了所有章节的学习！")
        scores = [max(progress[s]["scores"]) for s in progress if progress[s].get("scores")]
        if scores:
            avg = sum(scores) / len(scores)
            if avg >= 90:
                st.markdown(f"\U0001F3C6 **太厉害了！平均分 {avg:.0f}/100，初中数学完全没问题！**")
            elif avg >= 70:
                st.markdown(f"\U0001F44D **不错！平均分 {avg:.0f}/100，开学前可以再复习一下薄弱章节。**")
            else:
                st.markdown(f"\U0001F4AA **平均分 {avg:.0f}/100，建议重新学习分数较低的章节。**")


# ============================================================
# 主程序
# ============================================================
def main():
    init_session_state()

    page = st.sidebar.radio(
        "导航",
        ["\U0001F3E0 首页", "\U0001F4D6 学习", "\U0001F4DD 错题本", "\U0001F4CA 进度总览"],
        label_visibility="collapsed",
    )

    if page == "\U0001F3E0 首页":
        render_home()
    elif page == "\U0001F4D6 学习":
        render_sidebar()
        render_main()
    elif page == "\U0001F4DD 错题本":
        render_wrong_book()
    elif page == "\U0001F4CA 进度总览":
        render_progress()


if __name__ == "__main__":
    main()
