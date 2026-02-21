import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ================== CUSTOM CSS ==================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Section Title */
.section-title {
    font-size: 26px;
    font-weight: 700;
    background: linear-gradient(90deg, #6C63FF, #00E5FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 15px;
}

/* Glass Card */
.glass-card {
    background: rgba(28, 31, 38, 0.9);
    padding: 20px;
    border-radius: 18px;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 30px rgba(108, 99, 255, 0.2);
    margin-bottom: 25px;
}

/* Metric Box */
.metric-box {
    background: #111827;
    padding: 18px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #374151;
}

/* Chart container */
.chart-container {
    background: rgba(28, 31, 38, 0.85);
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.15);
    margin-bottom: 30px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("<div class='section-title'>📊 Learning Analytics Dashboard</div>", unsafe_allow_html=True)

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
        st.write(e)
        st.stop()

if res.status_code != 200:
    st.error(f"Backend error: {res.status_code}")
    st.write(res.text)
    st.stop()

data = res.json()

daily_data = data.get("daily_avg", [])
students = data.get("student_progress", [])

# =========================
# METRIC SUMMARY
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='metric-box'>👥 นักศึกษาทั้งหมด<br><h2>{}</h2></div>".format(len(students)), unsafe_allow_html=True)

with col2:
    total_attempts = sum(len(s.get("scores", [])) for s in students)
    st.markdown("<div class='metric-box'>📝 จำนวนครั้งทำแบบฝึกหัด<br><h2>{}</h2></div>".format(total_attempts), unsafe_allow_html=True)

with col3:
    if daily_data:
        avg_overall = sum(d["avg_score"] for d in daily_data) / len(daily_data)
        avg_overall = round(avg_overall, 2)
    else:
        avg_overall = 0
    st.markdown("<div class='metric-box'>📊 คะแนนเฉลี่ยรวม<br><h2>{}</h2></div>".format(avg_overall), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# DAILY AVERAGE CHART
# =========================

st.markdown("<div class='section-title'>📈 คะแนนเฉลี่ยรายวัน</div>", unsafe_allow_html=True)

if not daily_data:
    st.info("ยังไม่มีข้อมูลคะแนนรายวัน")
else:
    daily_df = pd.DataFrame(daily_data)

    if not daily_df.empty:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        fig, ax = plt.subplots()
        ax.plot(daily_df["date"], daily_df["avg_score"], marker="o")
        ax.set_ylabel("Average Score")
        ax.set_xlabel("Date")
        plt.xticks(rotation=45)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# STUDENT PROGRESS
# =========================

st.markdown("<div class='section-title'>📊 แนวโน้มพัฒนาการรายบุคคล</div>", unsafe_allow_html=True)

if not students:
    st.info("ยังไม่มีข้อมูลนักศึกษา")
else:
    for student in students:
        scores = student.get("scores", [])
        name = student.get("name", "Unknown")

        if scores:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            fig, ax = plt.subplots()
            ax.plot(scores, marker="o")
            ax.set_title(name)
            ax.set_ylabel("Score")
            ax.set_xlabel("Attempt")
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.write(f"{name} ยังไม่มีข้อมูลคะแนน")