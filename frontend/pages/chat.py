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
    text-align: right;
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

# ================= INITIALIZE SESSION =================
if "history" not in st.session_state:
    st.session_state.history = []

if "conversation_id" not in st.session_state:
    # สร้าง conversation ใหม่อัตโนมัติ
    res = requests.post(
        f"{BASE_URL}/conversation/new",
        json={"user_id": user["id"]}
    )
    st.session_state.conversation_id = res.json()["conversation_id"]

if "prev_level" not in st.session_state:
    st.session_state.prev_level = 1

# ================= SIDEBAR =================
with st.sidebar:

    st.markdown("## 👤 บัญชีผู้ใช้")
    st.write(f"**ชื่อ:** {user.get('name')}")
    st.write(f"**Role:** {user.get('role')}")

    st.divider()

    level = st.session_state.get("level", 1)
    st.markdown("### 📈 Level")
    st.progress(level / 5)
    st.markdown(
        f"<div class='level-badge'>Level {level}/5</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # ===== NEW CHAT =====
    if st.button("➕ New Chat"):
        res = requests.post(
            f"{BASE_URL}/conversation/new",
            json={"user_id": user["id"]}
        )
        st.session_state.conversation_id = res.json()["conversation_id"]
        st.session_state.history = []
        st.rerun()

    st.divider()

    # ===== LOAD CONVERSATIONS =====
    res = requests.get(
        f"{BASE_URL}/conversations",
        params={"user_id": user["id"]}
    )

    conversations = res.json()

    st.markdown("### 🕘 ประวัติการสนทนา")

    for c in conversations:
        if st.button(f"💬 Chat {c['id']}", key=f"convo_{c['id']}"):
            st.session_state.conversation_id = c["id"]

            # โหลดข้อความจาก backend
            msg_res = requests.get(
                f"{BASE_URL}/conversation/messages",
                params={
                    "conversation_id": c["id"],
                    "user_id": user["id"]
                }
            )

            st.session_state.history = msg_res.json()
            st.rerun()

    st.divider()

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("pages/login.py")

    if user.get("role") == "admin":
        st.page_link("pages/admin_dashboard.py", label="📊 Dashboard")

# ================= HEADER =================
st.markdown(
    "<div class='main-title'>💬 AI Calculus Tutor</div>",
    unsafe_allow_html=True
)

st.markdown(
    f"<p style='text-align:center;color:#A5B4FC;'>กำลังใช้งานในชื่อ {user.get('name')}</p>",
    unsafe_allow_html=True
)

# ================= DISPLAY CHAT =================
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
                    "user_id": user["id"],
                    "message": msg,
                    "conversation_id": st.session_state.conversation_id
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

    st.session_state.history.append(
        {"role": "assistant", "content": reply}
    )

    st.rerun()