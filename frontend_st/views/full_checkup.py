import streamlit as st
from services.checkup_services import get_diabetes_service, get_heart_service, get_stroke_service

def render_page():
    # --- Custom CSS for Full Checkup ---
    st.markdown("""
    <style>
    .section-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 1px solid #f3f4f6;
    }
    .result-alert {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .result-alert.safe {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    .result-alert.danger {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    .footer-ubm {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        color: #6b7280;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🩺 Full Health Checkup")
    st.markdown("Isi data kesehatan lengkap Anda untuk mendapatkan prediksi risiko **Diabetes**, **Penyakit Jantung**, dan **Stroke** secara bersamaan.")

    # Instantiate Services
    diabetes_service = get_diabetes_service()
    heart_service = get_heart_service()
    stroke_service = get_stroke_service()

    # --- Form Input Section ---
    with st.form("full_checkup_form"):
        st.markdown("### 📝 Data Diri & Gaya Hidup")
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Umur (Tahun)", min_value=1, max_value=120, value=30)
            sex = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            marital = st.selectbox("Status Pernikahan", ["Belum Menikah", "Menikah"])
            work = st.selectbox("Tipe Pekerjaan", ["Private (Swasta)", "Self-employed (Wiraswasta)", "PNS (Govt)", "Anak-anak", "Belum Bekerja"])
        with c2:
            residence = st.selectbox("Tipe Tempat Tinggal", ["Perkotaan (Urban)", "Pedesaan (Rural)"])
            smoke = st.selectbox("Status Merokok", ["Pernah Merokok", "Tidak Pernah Merokok", "Merokok Aktif", "Tidak Diketahui"])
    
        st.markdown("---")
        st.markdown("### 🏥 Indikator Medis Umum")
        c1, c2, c3 = st.columns(3)
        with c1:
            bmi = st.number_input("BMI (Body Mass Index)", 10.0, 50.0, 25.0, help="Perhitungan berat badan (kg) dibagi kuadrat tinggi badan (m).")
            glucose = st.number_input("Rata-rata Gula Darah (mg/dL)", 50.0, 300.0, 100.0)
        with c2:
            hypertension = st.checkbox("Riwayat Hipertensi / Darah Tinggi")
            heart_disease = st.checkbox("Riwayat Penyakit Jantung")
        with c3:
            bp = st.number_input("Tekanan Darah (Trestbps) mmHg", 80, 200, 120)

        st.markdown("---")
        st.markdown("### ❤️ Spesifik Jantung (Heart Disease)")
        c1, c2 = st.columns(2)
        with c1:
             cp = st.selectbox("Tipe Nyeri Dada (CP)", [0, 1, 2, 3], format_func=lambda x: f"Tipe {x} (Skala Klinis)")
             chol = st.number_input("Kolesterol (mg/dl)", 100, 600, 200)
             fbs = st.selectbox("Gula Darah Puasa > 120 mg/dl?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
             restecg = st.selectbox("Resting ECG (Hasil EKG)", [0, 1, 2], help="0: Normal, 1: Kelainan ST-T, 2: Hipertrofi ventrikel kiri")
        with c2:
             thalach = st.number_input("Detak Jantung Maksimum", 60, 220, 150)
             exang = st.selectbox("Angina (Nyeri Dada) Akibat Olahraga?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
             oldpeak = st.number_input("ST Depression (Oldpeak)", 0.0, 10.0, 1.0)
             slope = st.selectbox("Slope ST Segment", [0, 1, 2])
             ca = st.selectbox("Jumlah Pembuluh Utama (0-3)", [0, 1, 2, 3])
             thal = st.selectbox("Thalassemia", [0, 1, 2, 3], format_func=lambda x: ["Unknown", "Normal", "Fixed Defect", "Reversible Defect"][x] if x < 4 else f"Type {x}")

        st.markdown("---")
        submitted = st.form_submit_button("🔍 Analisis Kesehatan Lengkap", type="primary", use_container_width=True)

    # --- Submission Logic ---
    if submitted:
        with st.spinner("Memproses data di semua model prediksi..."):
            
            # Prepare Data Dictionary
            sex_val = 1 if sex == "Laki-laki" else 0
            
            # Clean inputs for mapping
            work_clean = work.split(" (")[0]
            residence_clean = residence.split(" (")[0]
            
            # Mapping smoke: 'Pernah Merokok', ... to EN keys
            smoke_map_input = {
                "Pernah Merokok": "formerly smoked",
                "Tidak Pernah Merokok": "never smoked", 
                "Merokok Aktif": "smokes",
                "Tidak Diketahui": "Unknown"
            }
            smoke_clean = smoke_map_input.get(smoke, "Unknown")

            data_payload = {
                "age": age,
                "sex": sex_val,
                "bmi": bmi,
                "glucose": glucose,
                "bloodpressure": bp,
                "hypertension": 1 if hypertension else 0,
                "heartdisease": 1 if heart_disease else 0,
                "maritalstatus": 1 if marital == "Menikah" else 0,
                "worktype": work_map(work_clean),
                "residence": 1 if residence_clean == "Urban" else 0,
                "smoke": smoke_internal_map(smoke_clean),
                "cp": cp,
                "chol": chol,
                "fbs": fbs,
                "restecg": restecg,
                "thalach": thalach,
                "exang": exang,
                "oldpeak": oldpeak,
                "slope": slope,
                "ca": ca,
                "thal": thal
            }
            
            res_diabetes = diabetes_service.predict(data_payload)
            res_heart = heart_service.predict(data_payload)
            res_stroke = stroke_service.predict(data_payload)
            
            # --- Display Results ---
            st.markdown("### 📊 Hasil Analisis")
            
            t1, t2, t3 = st.tabs(["🍬 Diabetes", "❤️ Jantung", "🧠 Stroke"])
            
            with t1:
                display_result_card("Diabetes", res_diabetes, "diabetes")
            
            with t2:
                display_result_card("Penyakit Jantung", res_heart, "heartd")
            
            with t3:
                display_result_card("Stroke", res_stroke, "stroke")
    
    # --- Footer UBM Ancol ---
    st.markdown("""
    <div class="footer-ubm">
        <p><strong>Universitas Bunda Mulia Kampus Ancol</strong></p>
        <p>MediScope V1 - TSDN 2024 Competition Project</p>
    </div>
    """, unsafe_allow_html=True)

def work_map(w):
    mapping = {
        "Private": "privatejob", 
        "Self-employed": "selfemp", 
        "Govt_job": "govtemp", 
        "Children": "children", 
        "PNS": "govtemp", # Indo alias
        "Never_worked": "never_worked",
        "Belum Bekerja": "never_worked"
    }
    return mapping.get(w, "privatejob")

def smoke_internal_map(s):
    # This maps the EN display string to the EN db key format (often with underscore)
    return s.replace(" ", "_")

def display_result_card(title, res, key_suffix):
    if "error" in res:
        st.error(f"Gagal memuat hasil {title}: {res['error']}")
        return

    pred_key = f"prediksi_{key_suffix}"
    adv_key = f"saran_{key_suffix}"
    risk_key = f"faktor_risiko_{key_suffix}"
    
    prediction_text = res.get(pred_key, "Tidak ada data")
    
    # Styling based on positive/negative
    is_safe = "tidak" in prediction_text.lower()
    alert_class = "safe" if is_safe else "danger"
    icon = "✅" if is_safe else "⚠️"
    
    st.markdown(f"""
    <div class="result-alert {alert_class}">
        {icon} {prediction_text}
    </div>
    """, unsafe_allow_html=True)
        
    with st.expander("💡 Saran & Pencegahan", expanded=not is_safe):
        st.write(res.get(adv_key, "-"))
        
    with st.expander("🔍 Faktor Risiko Terdeteksi"):
        st.write(res.get(risk_key, "-"))
