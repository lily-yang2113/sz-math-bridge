# -*- coding: utf-8 -*-
"""
猫咪管家 - 桌面宠物猫咪
包含猫咪状态管理、心情系统、动画和交互反馈
"""
CAT_PHOTO_PATH = "cat.jpg"

def _load_photo_b64():
    if CAT_PHOTO_PATH and Path(CAT_PHOTO_PATH).exists():
        try:
            with open(CAT_PHOTO_PATH, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return "data:image/jpeg;base64," + data
        except:
            return ""
    return ""

CAT_PHOTO_B64 = _load_photo_b64()
import json
import datetime
from pathlib import Path

# ============================================================
# 猫咪档案
# ============================================================
CAT_PROFILE = {
    "name": "谢贵圆",
    "age": "3岁",
    "personality": "高冷",
    "body_type": "肥胖",
}

# 猫咪照片路径（请替换为实际照片路径）
CAT_PHOTO_PATH = "cat.jpg"  # 猫咪照片路径


# ============================================================
# 猫咪心情管理器
# ============================================================
class CatMood:
    def __init__(self, data_dir):
        self.file = Path(data_dir) / "cat_mood.json"
        self.data = self._load()

    def _load(self):
        default = {"mood": "normal", "eye_size": "normal", "completion_rate": 0, "updated": ""}
        if self.file.exists():
            try:
                return json.loads(self.file.read_text(encoding="utf-8"))
            except:
                return default
        self.file.parent.mkdir(exist_ok=True)
        self.file.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")
        return default

    def update(self, completion_rate):
        """根据完成率更新心情"""
        if completion_rate > 80:
            mood, eyes = "happy", "big"
        elif completion_rate < 50:
            mood, eyes = "sad", "small"
        else:
            mood, eyes = "normal", "normal"
        self.data = {
            "mood": mood, "eye_size": eyes,
            "completion_rate": completion_rate,
            "updated": datetime.datetime.now().isoformat(),
        }
        self.file.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    @property
    def mood_class(self):
        return self.data.get("mood", "normal")

    @property
    def eye_class(self):
        return "cat-eyes-" + self.data.get("eye_size", "normal")


# ============================================================
# 猫咪 HTML + CSS 生成器
# ============================================================
def get_cat_styles():
    return """
<style>
.cat-box {
    background: linear-gradient(135deg, #fff 0%, #f8fff8 100%);
    border-radius: 16px; padding: 12px 10px 10px;
    text-align: center; cursor: pointer;
    box-shadow: 0 2px 12px rgba(82,183,136,0.15);
    border: 2px solid rgba(82,183,136,0.2);
    transition: all 0.3s ease;
    position: relative;
}
.cat-box:hover {
    box-shadow: 0 4px 20px rgba(82,183,136,0.25);
    transform: translateY(-2px);
}

/* 猫咪图片 */
.cat-img-wrap {
    display: inline-block;
    perspective: 500px;
}
.cat-img {
    width: 80px; height: 80px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
    transform-style: preserve-3d;
}
.cat-img.placeholder {
    font-size: 64px; line-height: 80px;
    background: #e8f5e9;
    display: inline-block;
}

/* 心情 - 眼睛大小效果用 transform 模拟 */
.cat-eyes-big { transform: scale(1.12); }
.cat-eyes-small { transform: scale(0.88); opacity: 0.7; filter: grayscale(0.3); }

/* 睡眠 Zzz */
.cat-zzz {
    font-size: 16px; color: #90be6d;
    animation: zzzFloat 2s ease-in-out infinite;
    display: inline-block;
}
@keyframes zzzFloat {
    0% { opacity: 0; transform: translateY(0) translateX(0); }
    50% { opacity: 1; transform: translateY(-12px) translateX(6px); }
    100% { opacity: 0; transform: translateY(-24px) translateX(12px); }
}

/* ===== 动画 ===== */
.cat-sleep {
    animation: catBreathe 3s ease-in-out infinite;
}
@keyframes catBreathe {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.04); }
}

.cat-jump {
    animation: catJump 0.6s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}
@keyframes catJump {
    0% { transform: translateY(0) scale(1,1); }
    30% { transform: translateY(-60px) scale(1,1); }
    50% { transform: translateY(-70px) scale(1.1,0.9); }
    70% { transform: translateY(-40px) scale(1,1); }
    100% { transform: translateY(0) scale(1,1); }
}

.cat-spin {
    animation: catSpin 0.8s ease;
}
@keyframes catSpin {
    0% { transform: rotate(0deg) scale(1); }
    50% { transform: rotate(360deg) scale(1.3); }
    100% { transform: rotate(720deg) scale(1); }
}

.cat-scratch {
    animation: catScratch 0.4s ease;
}
@keyframes catScratch {
    0%, 100% { transform: translateX(0) rotate(0deg); }
    20% { transform: translateX(-8px) rotate(-8deg); }
    40% { transform: translateX(8px) rotate(8deg); }
    60% { transform: translateX(-6px) rotate(-5deg); }
    80% { transform: translateX(6px) rotate(5deg); }
}

.cat-dance {
    animation: catDance 0.8s ease infinite;
}
@keyframes catDance {
    0% { transform: translateY(0) rotate(0deg); }
    15% { transform: translateY(-20px) rotate(-10deg); }
    30% { transform: translateY(-10px) rotate(10deg); }
    45% { transform: translateY(-25px) rotate(-5deg); }
    60% { transform: translateY(-8px) rotate(5deg); }
    75% { transform: translateY(-15px) rotate(-8deg); }
    100% { transform: translateY(0) rotate(0deg); }
}

.cat-happy {
    animation: catHappy 0.5s ease;
}
@keyframes catHappy {
    0%, 100% { transform: scale(1) rotate(0deg); }
    25% { transform: scale(1.1) rotate(-3deg); }
    75% { transform: scale(1.15) rotate(3deg); }
}

/* 对话框 */
.cat-bubble {
    position: absolute; top: -32px; left: 50%;
    transform: translateX(-50%);
    background: #fff; border: 2px solid #52b788;
    border-radius: 14px; padding: 4px 14px;
    font-size: 12px; font-weight: 600; color: #2d6a4f;
    white-space: nowrap;
    box-shadow: 0 3px 12px rgba(0,0,0,0.12);
    z-index: 300;
    display: none;
    pointer-events: none;
}
.cat-bubble.show { display: block; }
.cat-bubble::after {
    content: ''; position: absolute; bottom: -8px; left: 50%;
    transform: translateX(-50%);
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid #52b788;
}

/* 档案弹窗 */
.cat-modal-overlay {
    display: none; position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.4);
    z-index: 9999;
    justify-content: center; align-items: center;
}
.cat-modal-overlay.show { display: flex; }
.cat-modal-card {
    background: #fff; border-radius: 24px; padding: 28px 32px;
    max-width: 280px; width: 90%;
    text-align: center;
    box-shadow: 0 12px 48px rgba(0,0,0,0.2);
    animation: modalPop 0.3s ease;
}
@keyframes modalPop {
    0% { transform: scale(0.8); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}
.cat-modal-card .cat-profile-img {
    width: 110px; height: 110px;
    border-radius: 50%; object-fit: cover;
    border: 4px solid #52b788;
    margin-bottom: 8px;
}
.cat-modal-card h3 {
    margin: 8px 0; color: #2d6a4f; font-size: 22px;
}
.cat-modal-card .info-row {
    margin: 4px 0; font-size: 15px; color: #555;
}
.cat-modal-card .info-row b { color: #333; }
.cat-modal-card .close-btn {
    margin-top: 14px;
    padding: 8px 28px;
    background: #52b788; color: #fff;
    border: none; border-radius: 20px;
    cursor: pointer; font-size: 15px; font-weight: 600;
    transition: background 0.2s;
}
.cat-modal-card .close-btn:hover { background: #40916c; }

/* 烟花粒子 */
.cat-fireworks {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none; z-index: 1000;
    overflow: hidden;
}
.firework-particle {
    position: absolute; width: 10px; height: 10px;
    border-radius: 50%;
    animation: particleFly 1s ease-out forwards;
    box-shadow: 0 0 6px rgba(255,200,50,0.6);
}
@keyframes particleFly {
    0% { transform: translate(0, 0) scale(1); opacity: 1; }
    100% { transform: translate(var(--dx), var(--dy)) scale(0); opacity: 0; }
}

/* 心情指示器 */
.cat-mood-bar {
    height: 4px; border-radius: 2px;
    background: #e0e0e0; margin: 6px 0 2px;
    overflow: hidden;
}
.cat-mood-fill {
    height: 100%; border-radius: 2px;
    transition: width 0.5s ease;
}
.cat-mood-happy .cat-mood-fill { background: #52b788; width: var(--rate); }
.cat-mood-sad .cat-mood-fill { background: #ef476f; width: var(--rate); }
.cat-mood-normal .cat-mood-fill { background: #ffd166; width: var(--rate); }
</style>"""


def get_cat_html(action="sleep", bubble_text="", show_fireworks=False, mood="normal", completion_rate=0):
    """生成猫咪 HTML"""
    has_photo = CAT_PHOTO_PATH and Path(CAT_PHOTO_PATH).exists()
    
    # 图片
    if has_photo:
        img_html = f'<img src="{CAT_PHOTO_PATH}" class="cat-img {mood}" id="cat-photo" onclick="showCatProfile()">'
    else:
        img_html = '<span class="cat-img placeholder" onclick="showCatProfile()">🐱</span>'
    
    # 动画类
    anim_class = f"cat-{action}" if action else ""
    
    # 对话框
    bubble_class = "cat-bubble show" if bubble_text else "cat-bubble"
    
    # Zzz（睡觉时）
    zzz_html = '<div class="cat-zzz">💤</div>' if action == "sleep" else ""
    
    # 烟花
    fireworks_html = ""
    if show_fireworks:
        import random
        particles = []
        colors = ["#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff", "#ff6bcb", "#ff9f43"]
        for _ in range(30):
            dx = random.randint(-150, 150)
            dy = random.randint(-200, -50)
            color = random.choice(colors)
            size = random.randint(6, 14)
            left = random.randint(10, 90)
            top = random.randint(10, 60)
            delay = random.uniform(0, 0.3)
            particles.append(
                f'<div class="firework-particle" style="left:{left}%;top:{top}%;'
                f'--dx:{dx}px;--dy:{dy}px;background:{color};'
                f'width:{size}px;height:{size}px;animation-delay:{delay}s;"></div>'
            )
        fireworks_html = f'<div class="cat-fireworks">{"".join(particles)}</div>'
    
    # 心情指示
    mood_class_map = {"happy": "cat-mood-happy", "sad": "cat-mood-sad", "normal": "cat-mood-normal"}
    mood_css = mood_class_map.get(mood, "cat-mood-normal")
    mood_label = {"happy": "😊 开心", "sad": "😢 难过", "normal": "😐 平静"}.get(mood, "")
    
    html = f"""
    <div class="cat-box" id="cat-box">
        <div class="cat-img-wrap {anim_class}">
            {img_html}
        </div>
        {zzz_html}
        <div style="font-size:11px;color:#888;margin-top:2px;">
            点击查看档案
        </div>
        <div class="cat-bubble {bubble_class}">{bubble_text}</div>
    </div>
    <div class="cat-mood-bar {mood_css}" style="--rate:{completion_rate}%;">
        <div class="cat-mood-fill"></div>
    </div>
    <div style="font-size:11px;color:#888;text-align:center;">
        心情: {mood_label} | 完成率: {completion_rate:.0f}%
    </div>
    
    {fireworks_html}
    
    <!-- 档案弹窗 -->
    <div class="cat-modal-overlay" id="catProfileModal">
        <div class="cat-modal-card">
            {"".join([
                f'<img src="{CAT_PHOTO_PATH}" class="cat-profile-img">'
                if has_photo else '<span style="font-size:80px;display:block;">🐱</span>'
            ])}
            <h3>{CAT_PROFILE["name"]}</h3>
            <div class="info-row"><b>年龄</b>：{CAT_PROFILE["age"]}</div>
            <div class="info-row"><b>性格</b>：{CAT_PROFILE["personality"]}</div>
            <div class="info-row"><b>体型</b>：{CAT_PROFILE["body_type"]}</div>
            <div class="info-row"><b>心情</b>：{mood_label}</div>
            <button class="close-btn" onclick="closeCatProfile()">关闭</button>
        </div>
    </div>
    
    <script>
    function showCatProfile() {{
        document.getElementById('catProfileModal').classList.add('show');
    }}
    function closeCatProfile() {{
        document.getElementById('catProfileModal').classList.remove('show');
    }}
    </script>
    """
    return html


def init_cat_session():
    """初始化猫咪相关的 session_state 变量"""
    import streamlit as st
    if "cat_action" not in st.session_state:
        st.session_state.cat_action = "sleep"
    if "cat_bubble" not in st.session_state:
        st.session_state.cat_bubble = ""
    if "cat_consecutive" not in st.session_state:
        st.session_state.cat_consecutive = 0
    if "cat_fireworks" not in st.session_state:
        st.session_state.cat_fireworks = False
    if "cat_mood_mgr" not in st.session_state:
        pass  # 由外部初始化
    if "cat_profile" not in st.session_state:
        st.session_state.cat_profile = False


def trigger_cat_action(action, bubble="", reset_after=3):
    """触发猫咪动作"""
    import streamlit as st
    st.session_state.cat_action = action
    st.session_state.cat_bubble = bubble


def clear_cat_action():
    """清除猫咪动作（恢复睡觉）"""
    import streamlit as st
    st.session_state.cat_action = "sleep"
    st.session_state.cat_bubble = ""
    st.session_state.cat_fireworks = False


def on_correct_answer():
    """答对题时触发"""
    import streamlit as st
    st.session_state.cat_consecutive += 1
    if st.session_state.cat_consecutive >= 3:
        trigger_cat_action("spin", "🎆 连续答对3题！太厉害了！")
        st.session_state.cat_fireworks = True
        st.session_state.cat_consecutive = 0
    else:
        trigger_cat_action("jump", "🌟 太棒了！")


def on_wrong_answer():
    """答错题时触发"""
    import streamlit as st
    st.session_state.cat_consecutive = 0
    trigger_cat_action("scratch", "再想想哦~")


def on_all_done():
    """全部完成时触发"""
    import streamlit as st
    trigger_cat_action("dance", "🎵 全部学完啦！")
    st.session_state.cat_fireworks = True
    st.session_state.cat_consecutive = 0
    clear_cat_action()
    clear_cat_action()


def update_cat_mood(progress, total):
    """更新猫咪心情"""
    import streamlit as st
    if total > 0:
        rate = progress / total * 100
    else:
        rate = 0
    mgr = CatMood(Path(__file__).parent / "data")
    mgr.update(rate)
    return mgr
