import streamlit as st

# Page Config
st.set_page_config(
    page_title="MediScope - Pantau Kesehatan Anda",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Global CSS ---
st.markdown("""
<style>
    /* Global Font and Colors */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Button Styling */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Customize Primary Color (if not set in config.toml) */
    :root {
        --primary-color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# --- Navigation Logic ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("MediScope")
st.sidebar.caption("v1.0.0 - UBM Kampus Ancol")
st.sidebar.markdown("---")

# Navigation Buttons
# Using st.sidebar.button for navigation
def nav_button(label, page_name, icon=""):
    is_active = st.session_state.page == page_name
    type_ = "primary" if is_active else "secondary"
    if st.sidebar.button(f"{icon} {label}", key=f"nav_{page_name}", use_container_width=True, type=type_):
        st.session_state.page = page_name
        st.rerun()

nav_button("Beranda", "Home", "🏠")
nav_button("Quick Checkup", "Quick Checkup", "⚡")
nav_button("Full Checkup", "Full Checkup", "🩺")

st.sidebar.markdown("---")
st.sidebar.info(
    "**Disclaimer Medis:**\n\n"
    "MediScope menggunakan AI untuk estimasi awal. "
    "Hasil **bukan diagnosis medis**. Segera hubungi dokter jika Anda mengalami gejala serius."
)

# --- Page Routing ---
if st.session_state.page == "Home":
    from views import home
    home.render_page()
elif st.session_state.page == "Quick Checkup":
    from views import quick_checkup
    quick_checkup.render_page()
elif st.session_state.page == "Full Checkup":
    from views import full_checkup
    full_checkup.render_page()
