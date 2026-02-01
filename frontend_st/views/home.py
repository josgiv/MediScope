import streamlit as st
from PIL import Image
import requests
from io import BytesIO

def render_page():
    # --- Custom CSS for Home Page ---
    st.markdown("""
    <style>
    /* Hero Section */
    .hero-container {
        padding: 4rem 1rem;
        text-align: center;
        background: linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
        border-radius: 20px;
        margin-bottom: 3rem;
    }
    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        line-height: 1.1 !important;
        color: #1e3a8a;
        margin-bottom: 1rem;
        background: -webkit-linear-gradient(45deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.25rem !important;
        color: #64748b;
        margin-bottom: 2.5rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Stats/Cards */
    .card-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .card-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-color: #3b82f6;
    }
    .card-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background-color: #eff6ff;
        width: 60px;
        height: 60px;
        line-height: 60px;
        border-radius: 50%;
        margin-left: auto;
        margin-right: auto;
    }
    .card-text {
        font-weight: 600;
        color: #334155;
    }

    /* FAQ Section */
    .faq-header {
        text-align: center;
        margin-top: 3rem;
        margin-bottom: 2rem;
        color: #0f172a;
        font-weight: 700;
    }

    /* Footer */
    .footer {
        background-color: #1e293b;
        color: #f8fafc;
        padding: 3rem 1rem;
        margin-top: 5rem;
        border-radius: 20px 20px 0 0;
        text-align: center;
    }
    .footer h3 {
        margin-top: 0;
        color: #3b82f6;
    }
    .footer-text {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Hero Section ---
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">MediScope</div>
        <div class="hero-subtitle">Platform deteksi dini kesehatan berbasis AI yang dirancang untuk memberikan analisis cepat dan akurat tentang risiko kesehatan Anda.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons
    c1, c2, c3 = st.columns([1, 1, 0.1]) 
    with c1:
        st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
        if st.button("⚡ Quick Checkup", type="primary", use_container_width=True):
            st.session_state.page = "Quick Checkup"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        if st.button("🩺 Full Checkup", use_container_width=True):
            st.session_state.page = "Full Checkup"
            st.rerun()
    
    # --- Disease List Section ---
    st.markdown("---")
    st.subheader("Cakupan Deteksi Penyakit")
    st.markdown("Model kami dilatih untuk mendeteksi berbagai indikator risiko kesehatan:")
    
    diseases = [
        {"name": "Penyakit Jantung", "icon": "❤️"},
        {"name": "Diabetes", "icon": "🍬"},
        {"name": "Stroke", "icon": "🧠"},
        {"name": "Hipertensi", "icon": "📉"},
        {"name": "Alergi", "icon": "🤧"},
        {"name": "Penyakit Paru", "icon": "🫁"},
        {"name": "Hepatitis", "icon": "🧪"},
        {"name": "Arthritis", "icon": "🦴"},
    ]

    # Display in grid
    rows = [diseases[i:i+4] for i in range(0, len(diseases), 4)]
    for row in rows:
        cols = st.columns(4)
        for i, d in enumerate(row):
            with cols[i]:
                st.markdown(f"""
                <div class="card-box">
                    <div class="card-icon">{d['icon']}</div>
                    <div class="card-text">{d['name']}</div>
                </div>
                """, unsafe_allow_html=True)

    # --- Features Section ---
    st.markdown("---")
    
    # Using columns for features
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.markdown("### 🚀 Cepat & Mudah")
        st.write("Dapatkan hasil analisis awal hanya dalam hitungan detik setelah memasukkan gejala atau data klinis Anda.")
        
    with f2:
        st.markdown("### 🤖 Berbasis AI")
        st.write("Didukung oleh model Machine Learning yang telah dilatih dengan ribuan dataset medis terverifikasi.")
        
    with f3:
        st.markdown("### 🔒 Privasi Terjaga")
        st.write("Data yang Anda masukkan hanya diproses untuk keperluan analisis dan tidak disimpan secara permanen.")

    # --- FAQ Section ---
    st.markdown("<h2 class='faq-header'>Pertanyaan Umum</h2>", unsafe_allow_html=True)
    
    faq = {
        "Apa Itu MediScope?": "MediScope adalah aplikasi prediksi kesehatan berbasis kecerdasan buatan yang dikembangkan untuk mendeteksi risiko penyakit secara dini.",
        "Apakah akurat?": "Aplikasi ini memberikan estimasi probabilitas berdasarkan data statistik. Namun, ini **bukan** pengganti diagnosis medis profesional.",
        "Apakah gratis?": "Ya, MediScope dapat diakses secara gratis untuk membantu masyarakat sadar akan kesehatan.",
        "Bagaimana jika hasil risiko tinggi?": "Kami sangat menyarankan Anda untuk segera berkonsultasi dengan dokter atau spesialis untuk pemeriksaan lebih lanjut.",
    }

    for question, answer in faq.items():
        with st.expander(question):
            st.write(answer)

    # --- Footer ---
    st.markdown("""
    <div class="footer">
        <h3>MediScope</h3>
        <p class="footer-text">Project Kompetisi TSDN 2024</p>
        <p class="footer-text"><strong>Universitas Bunda Mulia Kampus Ancol</strong></p>
        <p class="footer-text" style="margin-top: 1rem; font-size: 0.8rem;">
            Disclaimer: Hasil analisis ini adalah prediksi statistik dan tidak boleh dianggap sebagai diagnosis medis resmi.
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_home():
    render_page()
