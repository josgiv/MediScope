import streamlit as st
from services.checkup_services import get_quick_checkup_service
from utils.translations import SYMPTOM_TRANSLATIONS

def render_page():
    # --- Custom CSS for Quick Checkup ---
    st.markdown("""
    <style>
    .stSelectbox label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f2937;
    }
    .result-card {
        background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3b82f6;
        margin-top: 2rem;
    }
    .result-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    .result-desc {
        color: #4b5563;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    .footer-ubm {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        color: #6b7280;
        font-size: 0.9rem;
    }
    .tutorial-box {
        background-color: #e0f2fe;
        border: 1px solid #7dd3fc;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        color: #0369a1;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>⚡ Quick Checkup</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 2rem;'>Pilih gejala yang Anda rasakan untuk mendapatkan analisis awal kesehatan Anda secara cepat dan akurat.</p>", unsafe_allow_html=True)

    # --- Tutorial Section ---
    with st.expander("📘 Cara Menggunakan (Tutorial)"):
        st.markdown("""
        **Langkah-langkah melakukan pemeriksaan cepat:**
        1.  **Pilih Gejala Utama**: Pada kotak pilihan pertama, cari dan pilih gejala yang paling dominan atau paling mengganggu yang Anda rasakan.
        2.  **Pilih Gejala Tambahan**: Jika ada gejala lain, pilih pada kotak "Gejala Tambahan" berikutnya.
        3.  **Otomasi Opsi**: Sistem akan otomatis menghapus gejala yang sudah Anda pilih dari daftar berikutnya agar tidak terjadi duplikasi.
        4.  **Analisa**: Setelah selesai memilih semua gejala yang dirasakan (minimal 1), klik tombol **"🔍 Analisa Gejala Sekarang"**.
        5.  **Hasil**: Baca hasil prediksi, deskripsi penyakit, dan saran pencegahan yang muncul di bawah.
        """)
        st.info("Catatan: Semakin lengkap gejala yang Anda masukkan, semakin akurat hasil analisisnya.")

    # Instantiate Service
    checkup = get_quick_checkup_service()

    if not checkup.model:
        st.error("Model Quick Checkup tidak dapat dimuat. Harap periksa konfigurasi backend.")
        return

    # --- Symptom Selection Logic ---
    # Get all symptoms from the service (which matches the model features)
    symptom_options = []
    for key in checkup.symptom_weights.keys():
        label = SYMPTOM_TRANSLATIONS.get(key, key.replace("_", " ").title())
        symptom_options.append((label, key))
    
    # Sort by Label (Indonesian)
    symptom_options.sort(key=lambda x: x[0])
    
    # Map labels back to keys
    options_map = {label: key for label, key in symptom_options}
    all_labels = [""] + list(options_map.keys())

    # Form Container
    with st.container():
        c1, c2 = st.columns(2, gap="large")
        
        # We need to manage the options for each selectbox dynamically.
        # Since Streamlit runs top-to-bottom, we can't easily make S1 depend on S4 without a rerun or callback.
        # To keep it simple and intuitive: S2 excludes S1. S3 excludes S1+S2. S4 excludes S1+S2+S3.
        # This enforces a "fill in order" flow which is good for UX.
        
        with c1:
            # Symptom 1
            s1_label = st.selectbox("Gejala Utama", all_labels, key="s1", help="Pilih gejala yang paling dominan Anda rasakan.")
            
            # Symptom 2 options = All - S1
            ops2 = [x for x in all_labels if x == "" or x != s1_label]
            s2_label = st.selectbox("Gejala Tambahan 1", ops2, key="s2")

        with c2:
            # Symptom 3 options = All - S1 - S2
            ops3 = [x for x in all_labels if x == "" or x not in [s1_label, s2_label]]
            s3_label = st.selectbox("Gejala Tambahan 2", ops3, key="s3")
            
            # Symptom 4 options = All - S1 - S2 - S3
            ops4 = [x for x in all_labels if x == "" or x not in [s1_label, s2_label, s3_label]]
            s4_label = st.selectbox("Gejala Tambahan 3", ops4, key="s4")

    # --- Prediction Logic ---
    st.markdown("---")
    
    # Center the button
    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        analyze_btn = st.button("🔍 Analisa Gejala Sekarang", type="primary", use_container_width=True)

    if analyze_btn:
        # Resolve labels back to keys
        selected_labels = [s for s in [s1_label, s2_label, s3_label, s4_label] if s != ""]
        selected_keys = [options_map[l] for l in selected_labels]

        if not selected_keys:
            st.warning("⚠️ Harap pilih setidaknya satu gejala untuk memulai analisis.")
        else:
            with st.spinner("Sedang menganalisis gejala Anda dengan model AI..."):
                result = checkup.predict(selected_keys)

                if "error" in result:
                    st.error(f"Terjadi kesalahan: {result['error']}")
                else:
                    # --- Result Display ---
                    disease_name = result['Disease']
                    description = result["Description"]
                    precautions = result["Precautions"]

                    # Display Result Card
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-title">Hasil Prediksi: {disease_name}</div>
                        <div class="result-desc">{description}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.subheader("💡 Saran Pencegahan & Tindakan")
                    
                    if isinstance(precautions, list):
                        cols = st.columns(len(precautions))
                        for idx, p in enumerate(precautions):
                            with cols[idx % 4]: # Wrap if many
                                st.info(f"**{idx+1}.** {p.title()}") 
                    else:
                        st.info(str(precautions))

    # --- Footer UBM Ancol ---
    st.markdown("""
    <div class="footer-ubm">
        <p><strong>Universitas Bunda Mulia Kampus Ancol</strong></p>
        <p>MediScope V1 - TSDN 2024 Competition Project</p>
    </div>
    """, unsafe_allow_html=True)
