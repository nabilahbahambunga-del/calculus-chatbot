import streamlit as st
import requests

BASE_URL = "https://calculus-backend.onrender.com"

st.set_page_config(page_title="สมัครสมาชิก | PSU AI Tutor", page_icon="🎓")

# ================= UI STYLE =================
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stButton>button {
        background-color: #003366;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 45px;
        width: 100%;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("## 🎓 สมัครสมาชิก PSU AI Tutor")
st.markdown("ระบบผู้ช่วยสอนแคลคูลัสอัจฉริยะสำหรับนักศึกษามหาวิทยาลัยสงขลานครินทร์")
st.divider()

# ================= FORM =================
with st.form("register_form"):

    col1, col2 = st.columns(2)

    with col1:
        student_id = st.text_input("รหัสนักศึกษา (10 หลัก)")
        year = st.selectbox("ชั้นปี", [1, 2, 3, 4])

    with col2:
        name = st.text_input("ชื่อ-นามสกุล")
        major = st.text_input("สาขาวิชา")

    email = st.text_input("อีเมลมหาวิทยาลัย (ตัวอย่าง: 6789012345@psu.ac.th)")
    password = st.text_input("รหัสผ่าน", type="password")

    submit = st.form_submit_button("✅ สมัครสมาชิก")

# ================= SUBMIT LOGIC =================
if submit:

    if not student_id or not name or not email or not password or not major:
        st.error("⚠️ กรุณากรอกข้อมูลให้ครบทุกช่อง")
        st.stop()

    with st.spinner("กำลังดำเนินการสมัครสมาชิก..."):

        try:
            res = requests.post(
                f"{BASE_URL}/register",
                json={
                    "student_id": student_id,
                    "name": name,
                    "email": email,
                    "password": password,
                    "year": year,
                    "major": major
                }
            )

            data = res.json()

            if res.status_code == 200:
                st.success("🎉 สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ")
                st.balloons()
            else:
                st.error(data.get("detail", "เกิดข้อผิดพลาด"))

        except Exception:
            st.error("❌ ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้")