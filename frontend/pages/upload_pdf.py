import streamlit as st
import requests

user = st.session_state.user
if user["role"] != "admin":
    st.stop()

st.title("Upload PDF")

file = st.file_uploader("PDF", type=["pdf"])
if file:
    res = requests.post(
        "https://calculus-backend.onrender.com/upload_pdf",
        params={"user_id": user["id"]},
        files={"file": file}
    )
    st.success(res.json()["message"])
