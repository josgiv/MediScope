import streamlit as st
from PIL import Image
import requests
from io import BytesIO

def render_page():
    # --- Custom CSS for Styling ---
    st.markdown("""
    <style>
    .hero-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
    }
    .hero-subtitle {
        font-size: 1.5rem !important;
        color: #666;
        margin-bottom: 2rem;
    }
    .card-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .card-icon {
        font-size: 2rem;
        color: #3b82f6;
        margin-bottom: 10px;
    }
    .footer {
        background-color: #1a237e;
        color: white;
        padding: 40px;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Hero Section ---
    st.markdown('<div class="hero-title">Pantau resiko kesehatan anda!</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Medi<span style="color:#3b82f6">Scope</span></div>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Solusi paling jelas ada kesehatan yang anda perlukan.</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1.5, 1.5, 4]) # Adjusted to keep buttons side-by-side but not too far apart
    with c1:
        # width='stretch' replaces use_container_width=True for 2026+ Streamlit
        if st.button("Quick Checkup", type="primary", use_container_width=True):
            st.session_state.page = "Quick Checkup"
            st.rerun()
    with c2:
        if st.button("Full Checkup", use_container_width=True):
            st.session_state.page = "Full Checkup"
            st.rerun()
    
    # Doctor image removed as per user request ("GAUSA MAKE GAMBAR")


    # --- Disease List Section ---
    st.markdown("---")
    st.subheader("Atau, Pilih Penyakit Yang Ingin Anda Periksa")
    
    # Grid Layout for Cards
    diseases = [
        {"name": "Penyakit Jantung", "icon": "❤️"},
        {"name": "Diabetes", "icon": "🍬"},
        {"name": "Paru", "icon": "🫁"},
        {"name": "Tekanan Darah", "icon": "📉"},
        {"name": "Alergi", "icon": "🤧"},
        {"name": "Tuberculosis", "icon": "🦠"},
        {"name": "Hepatitis", "icon": "🧪"},
        {"name": "Arthritis", "icon": "🦴"},
    ]

    cols = st.columns(4)
    for i, d in enumerate(diseases):
        col = cols[i % 4]
        with col:
            st.markdown(f"""
            <div class="card-box">
                <div class="card-icon">{d['icon']}</div>
                <div style="font-weight:600;">{d['name']}</div>
            </div>
            """, unsafe_allow_html=True)

    # --- FAQ Section ---
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>Pertanyaan yang Sering Diajukan</h2>", unsafe_allow_html=True)
    
    faq = {
        "Apa Itu MediScope?": "MediScope adalah aplikasi prediksi kesehatan berbasis data yang memberikan estimasi potensi kondisi kesehatan pengguna berdasarkan data yang dimasukkan.",
        "Apakah hasil MediScope dapat digunakan sebagai diagnosis medis?": "Tidak. Hasil MediScope hanya sebagai referensi awal dan bukan diagnosis medis resmi. Konsultasikan dengan dokter.",
        "Data apa saja yang diperlukan?": "Usia, jenis kelamin, BMI, tekanan darah, gula darah, riwayat kesehatan, dll.",
        "Apakah data pengguna disimpan?": "Tidak, semua data hanya diproses sementara.",
        "Apakah MediScope akurat?": "Hasil adalah prediksi statistik, bukan jaminan.",
    }

    for question, answer in faq.items():
        with st.expander(question):
            st.write(answer)
    
    # --- About Project Section ---
    # --- About Project Section ---
    st.markdown("---")
    
    st.header("🏥 Tentang Proyek MediScope")
    st.write(
        "**MediScope** adalah inisiatif teknologi kesehatan yang dirancang untuk menjembatani kesenjangan "
        "antara keluhan awal pasien dengan identifikasi risiko medis yang cepat. Proyek ini dikembangkan "
        "sebagai solusi inovatif dalam kompetisi TSDN 2024."
    )
    
    st.subheader("🚀 Tujuan Utama")
    st.markdown("""
    *   **Deteksi Dini:** Membantu pengguna mengenali potensi risiko penyakit kritis (Jantung, Stroke, Diabetes) sebelum gejala menjadi parah.
    *   **Efisiensi Layanan:** Mengurangi beban antrean awal di fasilitas kesehatan dengan memberikan skrining mandiri yang dapat diakses kapan saja.
    *   **Edukasi Kesehatan:** Meningkatkan kesadaran masyarakat akan pentingnya parameter kesehatan seperti BMI, Gula Darah, dan Tekanan Darah.
    """)

    st.subheader("⚙️ Cara Kerja")
    st.markdown("MediScope menggunakan teknologi **Machine Learning** canggih yang telah dilatih dengan ribuan dataset medis terverifikasi. Sistem kami bekerja dengan:")
    st.markdown("""
    1.  **Input Data:** Pengguna memasukkan data gejala (untuk Quick Checkup) atau data klinis (untuk Full Checkup).
    2.  **Pemrosesan Model:** Data diproses menggunakan algoritma seperti *Random Forest* dan *Support Vector Classifier (SVC)* yang berjalan secara real-time.
    3.  **Analisis Prediktif:** Model mencocokkan pola data pengguna dengan pola penyakit yang telah dipelajari untuk menghasilkan persentase risiko.
    4.  **Rekomendasi:** Memberikan saran pencegahan dan tindakan lanjut yang relevan berdasarkan hasil prediksi.
    """)

    st.subheader("🔍 Cakupan Analisis")
    st.markdown("Aplikasi ini mencakup deteksi risiko untuk:")
    st.markdown("""
    *   **Penyakit Jantung:** Menganalisis nyeri dada, tekanan darah, kolesterol, dan EKG.
    *   **Diabetes:** Mengevaluasi kadar glukosa, insulin, BMI, dan usia.
    *   **Stroke:** Mempertimbangkan gaya hidup, riwayat penyakit jantung, dan hipertensi.
    *   **Penyakit Umum:** Deteksi cepat berbagai penyakit umum berdasarkan gejala fisik yang dirasakan.
    """)

    st.info("""
    **⚠️ Disclaimer Penting**
    
    Aplikasi ini adalah alat bantu skrining **BUKAN PENGGANTI DOKTER**. Hasil prediksi yang diberikan bersifat probabilistik dan statistik. 
    Diagnosis medis yang akurat memerlukan pemeriksaan fisik, tes laboratorium lengkap, dan interpretasi ahli medis profesional. 
    Segera hubungi fasilitas kesehatan terdekat jika Anda mengalami gejala darurat.
    """)


    # --- Footer ---
    st.markdown("""
    <div class="footer">
        <h3>MediScope</h3>
        <p>Jl. Lorem/No.1-5, Jl.Ring Area, Kec. Palembang, Jkt</p>
        <p>Copyright ©2024 MediScope. All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

def show_home():
    render_page()
