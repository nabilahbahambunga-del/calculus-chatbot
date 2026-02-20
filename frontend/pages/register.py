import streamlit as st
import requests

BASE_URL = "https://calculus-backend.onrender.com"

st.title("📝 Register")

student_id = st.text_input("Student ID")
name = st.text_input("Name")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

# ================== STEP 1: SEND OTP ==================
if st.button("ส่งรหัสยืนยัน (OTP)"):

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
        st.success("ส่ง OTP ไปยังอีเมลแล้ว 📧")
        st.session_state.pending_email = email
    else:
        st.error(res.json().get("detail", "เกิดข้อผิดพลาด"))

# ================== STEP 2: VERIFY OTP ==================
if "pending_email" in st.session_state:

    otp = st.text_input("กรอกรหัส OTP ที่ได้รับ")

    if st.button("ยืนยันการสมัคร"):

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