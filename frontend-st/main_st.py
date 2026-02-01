import streamlit as st

# Page Config
st.set_page_config(
    page_title="MediScope - Pantau Kesehatan Anda",
    page_icon="🏥",
    layout="wide",
)

# --- Navigation Logic ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("MediScope")
st.sidebar.markdown("---")

# Navigation Buttons with Active State Highlighting
# We use type="primary" for the active page, "secondary" for others.
# use_container_width=True makes them look like menu items.

if st.sidebar.button("🏠 Beranda", 
                     key="nav_home", 
                     use_container_width=True, 
                     type="primary" if st.session_state.page == "Home" else "secondary"):
    st.session_state.page = "Home"
    st.rerun()

if st.sidebar.button("⚡ Quick Checkup", 
                     key="nav_quick", 
                     use_container_width=True, 
                     type="primary" if st.session_state.page == "Quick Checkup" else "secondary"):
    st.session_state.page = "Quick Checkup"
    st.rerun()

if st.sidebar.button("🩺 Full Checkup", 
                     key="nav_full", 
                     use_container_width=True, 
                     type="primary" if st.session_state.page == "Full Checkup" else "secondary"):
    st.session_state.page = "Full Checkup"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(
    "**Disclaimer:**\n"
    "Hasil pemeriksaan ini hanya sebagai referensi awal. "
    "Segera konsultasikan dengan dokter untuk diagnosis medis yang akurat."
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
