import streamlit as st
import requests

st.set_page_config(layout="centered")

# ================== CSS ==================
st.markdown("""
<style>
.login-box {
    padding: 40px;
    background: #1C1F26;
    border-radius: 15px;
    box-shadow: 0px 0px 20px rgba(108,99,255,0.3);
}
.stTextInput>div>div>input {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='login-box'>", unsafe_allow_html=True)

st.title("🔐 Login")
student_id = st.text_input("รหัสนักศึกษา")
password = st.text_input("รหัสผ่าน", type="password")

if st.button("Login"):

    with st.spinner("กำลังเข้าสู่ระบบ..."):
        res = requests.post(
            "https://calculus-backend.onrender.com/login",
            json={
                "student_id": student_id,
                "password": password
            }
        )

    if res.status_code != 200:
        st.error("เข้าสู่ระบบไม่สำเร็จ")
        st.write(res.text)
        st.stop()

    data = res.json()

    st.session_state.user = data
    st.success("Login สำเร็จ 🎉")

    st.switch_page("app.py")

st.markdown("</div>", unsafe_allow_html=True)
