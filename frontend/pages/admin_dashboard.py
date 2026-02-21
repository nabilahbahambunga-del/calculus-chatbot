import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# =========================
# CLEAN MINIMAL CSS
# =========================
st.markdown("""
<style>

/* Page spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Section title */
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* Card style */
.dashboard-card {
    background: #ffffff;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    margin-bottom: 25px;
}

/* Small muted text */
.muted-text {
    color: #6b7280;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.markdown("## 📊 Learning Analytics Dashboard")
st.markdown("<div class='muted-text'>ภาพรวมผลการเรียนรู้ของนักศึกษา</div>", unsafe_allow_html=True)
st.divider()

# =========================
# AUTH CHECK
# =========================

if "user" not in st.session_state:
    st.error("กรุณาเข้าสู่ระบบก่อน")
    st.stop()

user = st.session_state.user
user_id = user.get("id")

if not user_id:
    st.error("ไม่พบ User ID")
    st.stop()

if user.get("role") != "admin":
    st.error("หน้านี้สำหรับ Admin เท่านั้น")
    st.stop()

# =========================
# CALL BACKEND
# =========================

with st.spinner("กำลังโหลดข้อมูล..."):
    try:
        res = requests.get(
            "https://calculus-backend.onrender.com/admin/dashboard",
            params={"user_id": user_id},
            timeout=10
        )
    except Exception as e:
        st.error("ไม่สามารถเชื่อมต่อ Backend ได้")
        st.stop()

if res.status_code != 200:
    st.error(f"Backend error: {res.status_code}")
    st.stop()

data = res.json()

# =========================
# DAILY AVERAGE SECTION
# =========================

st.markdown("<div class='section-title'>📈 กราฟคะแนนเฉลี่ยรายวัน</div>", unsafe_allow_html=True)

st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)

daily_data = data.get("daily_avg", [])

if not daily_data:
    st.info("ยังไม่มีข้อมูลคะแนนรายวัน")
else:
    daily_df = pd.DataFrame(daily_data)

    if not daily_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(daily_df["date"], daily_df["avg_score"], marker="o")
        ax.set_ylabel("Average Score")
        ax.set_xlabel("Date")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# STUDENT PROGRESS SECTION
# =========================

st.markdown("<div class='section-title'>📊 แนวโน้มพัฒนาการรายบุคคล</div>", unsafe_allow_html=True)

students = data.get("student_progress", [])

if not students:
    st.info("ยังไม่มีข้อมูลนักศึกษา")
else:
    for student in students:

        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)

        scores = student.get("scores", [])
        name = student.get("name", "Unknown")

        st.markdown(f"**{name}**")

        if scores:
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot(scores, marker="o")
            ax.set_ylabel("Score")
            ax.set_xlabel("Attempt")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.write("ยังไม่มีข้อมูลคะแนน")

        st.markdown("</div>", unsafe_allow_html=True)