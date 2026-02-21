import streamlit as st
import requests

st.set_page_config(layout="centered")

# =========================
# CLEAN UI CSS
# =========================
st.markdown("""
<style>
            
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.muted-text {
    color: #6b7280;
    font-size: 14px;
    margin-bottom: 1.5rem;
}

.upload-card {
    background: #ffffff;
    padding: 30px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}

.file-info {
    margin-top: 15px;
    font-size: 14px;
    color: #374151;
}

</style>
""", unsafe_allow_html=True)

# =========================
# AUTH CHECK
# =========================

if "user" not in st.session_state:
    st.error("กรุณาเข้าสู่ระบบก่อน")
    st.stop()

user = st.session_state.user

if user.get("role") != "admin":
    st.stop()

# =========================
# HEADER
# =========================

st.markdown("<div class='section-title'>📄 Upload PDF Document</div>", unsafe_allow_html=True)
st.markdown("<div class='muted-text'>อัปโหลดเอกสารเพื่อใช้เป็นแหล่งความรู้สำหรับ AI Tutor</div>", unsafe_allow_html=True)

st.markdown("<div class='upload-card'>", unsafe_allow_html=True)

# =========================
# FILE UPLOADER
# =========================

file = st.file_uploader("เลือกไฟล์ PDF", type=["pdf"])

if file:
    file_size = round(file.size / (1024 * 1024), 2)

    st.markdown(
        f"<div class='file-info'>"
        f"📎 <b>{file.name}</b><br>"
        f"ขนาดไฟล์: {file_size} MB"
        f"</div>",
        unsafe_allow_html=True
    )

    if st.button("Upload File"):

        with st.spinner("กำลังอัปโหลดไฟล์..."):
            try:
                res = requests.post(
                    "https://calculus-backend.onrender.com/upload_pdf",
                    params={"user_id": user["id"]},
                    files={"file": file},
                    timeout=60
                )

                if res.status_code == 200:
                    st.success(res.json().get("message", "Upload สำเร็จ"))
                else:
                    st.error("เกิดข้อผิดพลาดจาก Backend")
                    st.write(res.text)

            except Exception as e:
                st.error("ไม่สามารถเชื่อมต่อ Backend ได้")

st.markdown("</div>", unsafe_allow_html=True)