import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Learning Analytics Dashboard")

user = st.session_state.user

res = requests.get(
    "http://localhost:8000/admin/dashboard",
    params={"user_id": user["id"]}
)

data = res.json()

# ===== Daily Average Chart =====
st.markdown("## 📈 กราฟคะแนนเฉลี่ยรายวัน")

daily_df = pd.DataFrame(data["daily_avg"])

if not daily_df.empty:
    fig, ax = plt.subplots()
    ax.plot(daily_df["date"], daily_df["avg_score"], marker="o")
    ax.set_ylabel("Average Score")
    ax.set_xlabel("Date")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ===== Student Progress =====
st.markdown("## 📊 แนวโน้มพัฒนาการรายบุคคล")

for student in data["student_progress"]:
    if student["scores"]:
        fig, ax = plt.subplots()
        ax.plot(student["scores"], marker="o")
        ax.set_title(student["name"])
        ax.set_ylabel("Score")
        ax.set_xlabel("Attempt")
        st.pyplot(fig)
