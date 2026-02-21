import streamlit as st
import requests

st.set_page_config(layout="centered")

# ================== CUSTOM CSS ==================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

/* Center container */
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 90vh;
}

/* Glass card */
.login-box {
    width: 380px;
    padding: 45px;
    border-radius: 20px;
    background: rgba(28, 31, 38, 0.9);
    backdrop-filter: blur(15px);
    box-shadow: 0 0 40px rgba(108, 99, 255, 0.3);
    text-align: center;
}

/* Title gradient */
.login-title {
    font-size: 30px;
    font-weight: 700;
    background: linear-gradient(90deg, #6C63FF, #00E5FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 30px;
}

/* Input style */
.stTextInput>div>div>input {
    border-radius: 12px;
    padding: 10px;
    background-color: #111827;
    color: white;
    border: 1px solid #374151;
}

.stTextInput>div>div>input:focus {
    border: 1px solid #6C63FF;
    box-shadow: 0 0 10px #6C63FF;
}

/* Login button */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    padding: 10px;
    font-weight: 600;
    background: linear-gradient(90deg, #6C63FF, #00E5FF);
    color: white;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
}

.footer-text {
    margin-top: 20px;
    font-size: 13px;
    color: #9CA3AF;
}

</style>
""", unsafe_allow_html=True)

# ================== UI ==================

st.markdown("<div class='login-container'>", unsafe_allow_html=True)
st.markdown("<div class='login-box'>", unsafe_allow_html=True)

st.markdown("<div class='login-title'>🔐 AI Calculus Tutor</div>", unsafe_allow_html=True)

student_id = st.text_input("รหัสนักศึกษา")
password = st.text_input("รหัสผ่าน", type="password")

if st.button("Login"):

    if not student_id or not password:
        st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")
        st.stop()

    with st.spinner("กำลังเข้าสู่ระบบ..."):
        try:
            res = requests.post(
                "https://calculus-backend.onrender.com/login",
                json={
                    "student_id": student_id,
                    "password": password
                },
                timeout=20
            )

            if res.status_code != 200:
                st.error("เข้าสู่ระบบไม่สำเร็จ ❌")
                st.stop()

            data = res.json()

        except:
            st.error("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้")
            st.stop()

    st.session_state.user = data
    st.success("Login สำเร็จ 🎉")
    st.switch_page("app.py")

st.markdown("<div class='footer-text'>© 2026 PSU AI Tutor • Mathematics & Computer Science</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)