import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("📊 Learning Analytics Dashboard")

# =========================
# AUTH CHECK
# =========================

if "user" not in st.session_state:
    st.error("กรุณาเข้าสู่ระบบก่อน")
    st.stop()

user = st.session_state.user

# 🔥 สร้าง user_id ตรงนี้เลย
user_id = user.get("id")

if not user_id:
    st.error("ไม่พบ User ID")
    st.stop()

# เช็ค role
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
        st.write(e)
        st.stop()

if res.status_code != 200:
    st.error(f"Backend error: {res.status_code}")
    st.write(res.text)
    st.stop()

data = res.json()

# =========================
# DAILY AVERAGE CHART
# =========================

st.markdown("## 📈 กราฟคะแนนเฉลี่ยรายวัน")

daily_data = data.get("daily_avg", [])

if not daily_data:
    st.info("ยังไม่มีข้อมูลคะแนนรายวัน")
else:
    daily_df = pd.DataFrame(daily_data)

    if not daily_df.empty:
        fig, ax = plt.subplots()
        ax.plot(daily_df["date"], daily_df["avg_score"], marker="o")
        ax.set_ylabel("Average Score")
        ax.set_xlabel("Date")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# =========================
# STUDENT PROGRESS
# =========================

st.markdown("## 📊 แนวโน้มพัฒนาการรายบุคคล")

students = data.get("student_progress", [])

if not students:
    st.info("ยังไม่มีข้อมูลนักศึกษา")
else:
    for student in students:
        scores = student.get("scores", [])
        name = student.get("name", "Unknown")

        if scores:
            fig, ax = plt.subplots()
            ax.plot(scores, marker="o")
            ax.set_title(name)
            ax.set_ylabel("Score")
            ax.set_xlabel("Attempt")
            st.pyplot(fig)
        else:
            st.write(f"{name} ยังไม่มีข้อมูลคะแนน")