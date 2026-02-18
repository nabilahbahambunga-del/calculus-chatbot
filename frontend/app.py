import streamlit as st

st.set_page_config(
    page_title="PSU AI Calculus Tutor",
    page_icon="🎓",
    layout="wide"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#1C1F26,#11131A);
}
.stButton>button {
    border-radius: 10px;
    background: linear-gradient(90deg,#6C63FF,#4FC3F7);
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION CHECK =================
if "user" not in st.session_state:
    st.switch_page("pages/landing.py")
    st.stop()

user = st.session_state.get("user")

# กันกรณี user เป็น None
if not user:
    st.switch_page("pages/landing.py")
    st.stop()

# ================= SIDEBAR NAV =================
with st.sidebar:
    st.markdown("## 🎓 PSU AI Tutor")
    st.write(f"👤 {user.get('name', 'Guest')}")
    st.write(f"🔑 {user.get('role', 'student')}")

    st.divider()

    menu_options = (
        ["💬 Chat", "📊 Dashboard", "🚪 Logout"]
        if user.get("role") == "admin"
        else ["💬 Chat", "🚪 Logout"]
    )

    page = st.radio("📌 เมนู", menu_options)

# ================= PAGE ROUTING =================
if page == "💬 Chat":
    st.switch_page("pages/chat.py")

elif page == "📊 Dashboard":
    st.switch_page("pages/admin_dashboard.py")

elif page == "🚪 Logout":
    st.session_state.clear()
    st.switch_page("pages/landing.py")
