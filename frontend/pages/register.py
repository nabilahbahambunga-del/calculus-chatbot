import streamlit as st
import requests

BASE_URL = "https://calculus-backend.onrender.com"

st.title("📝 Register")

student_id = st.text_input("Student ID")
name = st.text_input("Name")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

# ---------------- SEND OTP ----------------
if st.button("📧 ส่งรหัส OTP"):

    if not student_id or not name or not email or not password:
        st.error("กรอกข้อมูลให้ครบก่อน")
        st.stop()

    with st.spinner("กำลังส่ง OTP..."):
        res = requests.post(
            f"{BASE_URL}/send-otp",
            json={
                "student_id": student_id,
                "name": name,
                "email": email,
                "password": password
            }
        )

    if res.status_code == 200:
        st.success("ส่ง OTP ไปยังอีเมลแล้ว 📩")
        st.session_state.pending_email = email
    else:
        st.error(res.json().get("detail", "เกิดข้อผิดพลาด"))

# ---------------- VERIFY OTP ----------------
if "pending_email" in st.session_state:

    otp = st.text_input("กรอกรหัส OTP")

    if st.button("✅ ยืนยันการสมัคร"):

        with st.spinner("กำลังตรวจสอบ OTP..."):
            res = requests.post(
                f"{BASE_URL}/verify-otp",
                json={
                    "email": st.session_state.pending_email,
                    "otp": otp
                }
            )

        if res.status_code == 200:
            st.success("สมัครสำเร็จ 🎉 กรุณา Login")
            del st.session_state.pending_email
        else:
            st.error(res.json().get("detail", "OTP ไม่ถูกต้อง"))