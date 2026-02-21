import streamlit as st
import requests
import time

st.set_page_config(layout="wide")

BASE_URL = "https://calculus-backend.onrender.com"

# ================= CUSTOM CSS =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

.main-title {
    text-align: center;
    font-size: 32px;
    font-weight: 700;
    background: linear-gradient(90deg, #6C63FF, #00E5FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

section[data-testid="stSidebar"] {
    background: rgba(28, 31, 38, 0.95);
    backdrop-filter: blur(10px);
}

.chat-bubble-user {
    background: #6C63FF;
    padding: 12px 16px;
    border-radius: 15px;
    margin-bottom: 10px;
    color: white;
}

.chat-bubble-ai {
    background: #1f2937;
    padding: 12px 16px;
    border-radius: 15px;
    margin-bottom: 10px;
    border: 1px solid #6C63FF;
}

.score-card {
    background: #111827;
    padding: 12px;
    border-radius: 12px;
    margin-top: 10px;
    border: 1px solid #374151;
}

.level-badge {
    background: linear-gradient(90deg, #6C63FF, #00E5FF);
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: bold;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION CHECK =================
if "user" not in st.session_state:
    st.switch_page("pages/login.py")
    st.stop()

user = st.session_state.get("user")

if not user:
    st.switch_page("pages/login.py")
    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("## 👤 บัญชีผู้ใช้")
    st.write(f"**ชื่อ:** {user.get('name', 'Unknown')}")
    st.write(f"**Role:** {user.get('role', 'student')}")

    st.divider()

    level = st.session_state.get("level", 1)

    st.markdown("### 📈 Level")
    st.progress(level / 5)
    st.markdown(
        f"<div class='level-badge'>Level {level}/5</div>",
        unsafe_allow_html=True
    )

    st.divider()

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("pages/login.py")

    if user.get("role") == "admin":
        st.divider()
        st.page_link("pages/admin_dashboard.py", label="📊 Dashboard")

# ================= HEADER =================
st.markdown(
    "<div class='main-title'>💬 AI Calculus Tutor</div>",
    unsafe_allow_html=True
)

st.markdown(
    f"<p style='text-align:center;color:#A5B4FC;'>กำลังใช้งานในชื่อ {user.get('name','')}</p>",
    unsafe_allow_html=True
)

# ================= CHAT HISTORY =================
if "history" not in st.session_state:
    st.session_state.history = []

if "prev_level" not in st.session_state:
    st.session_state.prev_level = 1

for m in st.session_state.history:
    if m["role"] == "user":
        st.markdown(
            f"<div class='chat-bubble-user'>{m['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='chat-bubble-ai'>{m['content']}</div>",
            unsafe_allow_html=True
        )

msg = st.chat_input("พิมพ์คำถามเกี่ยวกับแคลคูลัส...")

# ================= SEND MESSAGE =================
if msg:
    st.session_state.history.append({"role": "user", "content": msg})

    with st.spinner("🤖 AI กำลังคิด..."):
        try:
            res = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "user_id": user.get("id"),
                    "message": msg
                },
                timeout=30
            )

            if res.status_code != 200:
                st.error("Backend มีปัญหา กรุณาลองใหม่")
                st.stop()

            data = res.json()

        except:
            st.error("ไม่สามารถเชื่อมต่อ Backend ได้")
            st.stop()

    reply = data.get("reply", "ไม่มีคำตอบ")
    score = data.get("score", 0)
    correct = data.get("correct", False)
    level = data.get("level", 1)

    st.session_state.level = level

    # 🎉 Level Up Animation
    if level > st.session_state.prev_level:
        st.balloons()
        st.success("🎉 Level Up!")
        time.sleep(1)

    st.session_state.prev_level = level

    # ✅ แสดงคะแนนเฉพาะเมื่อมีการประเมินจริง
    if score > 0:
        score_html = f"""
        <div class='score-card'>
            📊 คะแนน: {score}/10 <br>
            {"✅ ถูกต้อง" if correct else "❌ ยังไม่ถูกต้อง"} <br>
            📈 Level ปัจจุบัน: {level}
        </div>
        """
        reply += score_html

    st.session_state.history.append(
        {"role": "assistant", "content": reply}
    )

    st.rerun()