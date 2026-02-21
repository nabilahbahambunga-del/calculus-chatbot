import streamlit as st
import requests

st.set_page_config(layout="centered")

# ================== CUSTOM CSS ==================
st.markdown("""
style>
[data-testid="stSidebar"] {display: none;}
header {visibility: hidden;}
footer {visibility: hidden;}

html, body, [class*="css"] {
    height: 100%;
}

.main {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

/* Card */
.login-card {
    width: 400px;
    padding: 50px;
    border-radius: 18px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    text-align: center;
}

/* Title */
.login-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 30px;
}

/* Input */
.stTextInput>div>div>input {
    border-radius: 12px;
    padding: 10px;
}

/* Button */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    padding: 10px;
    font-weight: 600;
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