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
    <h1>🎓 PSU AI Calculus Tutor</h1>
    <h3>Adaptive Learning System Powered by LLaMA</h3>
    <p>ระบบผู้ช่วยสอนอัจฉริยะ พร้อมวิเคราะห์พัฒนาการผู้เรียนแบบ Real-time</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🚀 คุณสมบัติเด่น")

col1, col2, col3 = st.columns(3)

col1.markdown('<div class="card">💬 AI Tutor</div>', unsafe_allow_html=True)
col2.markdown('<div class="card">📊 Learning Analytics</div>', unsafe_allow_html=True)
col3.markdown('<div class="card">🏆 Adaptive Level System</div>', unsafe_allow_html=True)

st.divider()

if st.button("🔐 เข้าสู่ระบบ"):
    st.switch_page("pages/login.py")
