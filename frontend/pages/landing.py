import streamlit as st

st.set_page_config(layout="wide")

st.markdown("""
<style>
.hero {
    padding: 80px;
    text-align: center;
    background: linear-gradient(135deg,#1e3c72,#2a5298,#6C63FF);
    color: white;
    border-radius: 15px;
}
.card {
    padding: 30px;
    background: #1C1F26;
    border-radius: 15px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🎓AI Calculus Tutor</h1>
    <h3>Artificial Intelligence Chatbot System for Calculus I Learning Guidance</h3>
    <p>ระบบแชทบอทปัญญาประดิษฐ์เพื่อแนะนำการเรียนรายวิชาแคลคูลัส I</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🚀 คุณสมบัติ")

col1, col2, col3 = st.columns(3)

col1.markdown('<div class="card">💬 AI Tutor</div>', unsafe_allow_html=True)
col2.markdown('<div class="card">📊 Learning Analytics</div>', unsafe_allow_html=True)
col3.markdown('<div class="card">🏆 Adaptive Level System</div>', unsafe_allow_html=True)

st.divider()

if st.button("🔐 เข้าสู่ระบบ"):
    st.switch_page("pages/login.py")
