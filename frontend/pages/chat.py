import streamlit as st
import requests
import time

st.set_page_config(layout="wide")

# ================= PRODUCTION BACKEND =================
BASE_URL = "https://calculus-backend.onrender.com"

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
    st.markdown("## 👤 บัญชีที่เข้าสู่ระบบ")
    st.write(f"**ชื่อ:** {user.get('name', 'Unknown')}")
    st.write(f"**Role:** {user.get('role', 'student')}")

    st.divider()

    level = st.session_state.get("level", 1)
    st.markdown("### 📈 Level")
    st.progress(level / 5)
    st.write(f"{level}/5")

    st.divider()

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("pages/login.py")

    if user.get("role") == "admin":
        st.divider()
        st.page_link("pages/admin_dashboard.py", label="📊 Dashboard")

# ================= HEADER =================
st.markdown(
    f"""
    <h2 style='text-align:center;'>💬 ห้องสนทนา</h2>
    <p style='text-align:center;color:#6C63FF;'>
    กำลังใช้งานในชื่อ {user.get('name', '')}
    </p>
    """,
    unsafe_allow_html=True
)

# ================= CHAT HISTORY =================
if "history" not in st.session_state:
    st.session_state.history = []

if "prev_level" not in st.session_state:
    st.session_state.prev_level = 1

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

msg = st.chat_input("ถามคำถามแคลคูลัส...")

# ================= SEND MESSAGE =================
if msg:
    st.session_state.history.append({"role": "user", "content": msg})

    with st.spinner("AI กำลังวิเคราะห์..."):
        try:
            res = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "user_id": user.get("id", 1),
                    "message": msg
                },
                timeout=30
            )

            if res.status_code != 200:
                st.error("Backend มีปัญหา กรุณาลองใหม่อีกครั้ง")
                st.stop()

            data = res.json()

        except Exception as e:
            st.error("ไม่สามารถเชื่อมต่อกับ Backend ได้")
            st.stop()

    reply = data.get("reply", "ไม่มีคำตอบ")
    score = data.get("score", 0)
    correct = data.get("correct", False)
    level = data.get("level", 1)

    st.session_state.level = level

    # 🎯 Animation Level Up
    if level > st.session_state.prev_level:
        st.balloons()
        st.success("🎉 Level Up!")
        time.sleep(1)

    st.session_state.prev_level = level

    result = f"\n\n📊 คะแนน: {score}/10"
    result += "\n✅ ถูกต้อง" if correct else "\n❌ ยังไม่ถูกต้อง"
    result += f"\n📈 Level ปัจจุบัน: {level}"

    reply += result

    st.session_state.history.append(
        {"role": "assistant", "content": reply}
    )

    st.rerun()
