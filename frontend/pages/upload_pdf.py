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
    max-width: 600px;
}

/* Title */
.page-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 6px;
}

.page-subtitle {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 30px;
}

/* File info inline */
.file-info {
    margin-top: 10px;
    font-size: 14px;
    color: #374151;
}

/* Clean Button */
.stButton>button {
    width: 100%;
    padding: 10px;
    border-radius: 8px;
    font-weight: 600;
    background-color: black;
    color: white;
    border: none;
}

.stButton>button:hover {
    background-color: #1f2937;
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
st.markdown("<div class='page-subtitle'>อัปโหลดเอกสารเพื่อใช้เป็นฐานความรู้</div>", unsafe_allow_html=True)

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
                data={"user_id": str(user["id"])}, 
                files={"file": file},
                timeout=300
            )

            st.write("Status:", res.status_code)
            st.write("Response:", res.text)

            if res.status_code == 200:
                st.success("Upload สำเร็จ 🎉")
            else:
                st.error("Upload ล้มเหลว")

        except Exception as e:
            st.error("Error:")
            st.write(str(e))

st.markdown("</div>", unsafe_allow_html=True)