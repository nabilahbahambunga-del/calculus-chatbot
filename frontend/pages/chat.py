import streamlit as st
import requests
import time

st.set_page_config(layout="wide")

user = st.session_state.user

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("## 👤 บัญชีที่เข้าสู่ระบบ")
    st.write(f"**ชื่อ:** {user['name']}")
    st.write(f"**Role:** {user['role']}")

    st.divider()

    level = st.session_state.get("level", 1)
    st.markdown("### 📈 Level")
    st.progress(level / 5)
    st.write(f"{level}/5")

    st.divider()

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("pages/login.py")

    if user["role"] == "admin":
        st.divider()
        st.page_link("pages/admin_dashboard.py", label="📊 Dashboard")

# ================= HEADER =================
st.markdown(
    f"""
    <h2 style='text-align:center;'>💬 ห้องสนทนา</h2>
    <p style='text-align:center;color:#6C63FF;'>
    กำลังใช้งานในชื่อ {user['name']}
    </p>
    """,
    unsafe_allow_html=True
)

if "history" not in st.session_state:
    st.session_state.history = []

if "prev_level" not in st.session_state:
    st.session_state.prev_level = 1

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

msg = st.chat_input("ถามคำถามแคลคูลัส...")

if msg:
    st.session_state.history.append({"role": "user", "content": msg})

    with st.spinner("AI กำลังวิเคราะห์..."):
        res = requests.post(
            "http://localhost:8000/chat",
            json={
                "user_id": user["id"],
                "message": msg
            }
        )

    data = res.json()
    reply = data["reply"]
    score = data["score"]
    correct = data["correct"]
    level = data["level"]

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
