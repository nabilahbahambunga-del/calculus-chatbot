import streamlit as st
import requests

st.title("Register")

data = {
    "email" : st.text_input("อีเมล"),
    "student_id": st.text_input("รหัสนักศึกษา"),
    "name": st.text_input("ชื่อ - สกุล"),
    "major": st.text_input("สาขาวิชา"),
    "year": st.number_input("ชั้นปี", 1, 4),
    "password": st.text_input("รหัสผ่าน", type="password")
}

if st.button("Register"):
    requests.post("https://calculus-backend.onrender.com/register", json=data)
    st.success("สมัครสำเร็จ")
