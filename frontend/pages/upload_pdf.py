import streamlit as st
import requests

st.set_page_config(layout="centered")

# =========================
# MINIMAL LUXURY CSS
# =========================
st.markdown("""
<style>

.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    max-width: 650px;
}

/* Title */
.page-title {
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 5px;
}

.page-subtitle {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 30px;
}

/* Card */
.card {
    padding: 30px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    background-color: #ffffff;
}

/* File info */
.file-box {
    margin-top: 15px;
    padding: 15px;
    border-radius: 10px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    font-size: 14px;
}

/* Button clean style */
.stButton>button {
    width: 100%;
    border-radius: 10px;
    padding: 10px;
    font-weight: 600;
    background-color: black;
    color: white;
    border: none;
}

.stButton>button:hover {
    background-color: #111827;
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

st.markdown("<div class='page-title'>Upload PDF Document</div>", unsafe_allow_html=True)
st.markdown("<div class='page-subtitle'>อัปโหลดเอกสารเพื่อใช้เป็นฐานความรู้ของ AI Tutor</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)

# =========================
# FILE UPLOADER
# =========================

file = st.file_uploader("เลือกไฟล์ PDF", type=["pdf"])

if file:
    size_mb = round(file.size / (1024 * 1024), 2)

    st.markdown(
        f"""
        <div class='file-box'>
            <b>{file.name}</b><br>
            ขนาดไฟล์: {size_mb} MB
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Upload File"):

        with st.spinner("กำลังอัปโหลด..."):
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

            except:
                st.error("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้")

st.markdown("</div>", unsafe_allow_html=True)