import streamlit as st
import requests

st.title("Register")

data = {
    "student_id": st.text_input("Student ID"),
    "name": st.text_input("Name"),
    "major": st.text_input("Major"),
    "year": st.number_input("Year", 1, 6),
    "password": st.text_input("Password", type="password")
}

if st.button("Register"):
    requests.post("http://localhost:8000/register", json=data)
    st.success("สมัครสำเร็จ")
