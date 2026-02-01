import streamlit as st
from services.checkup_services import get_diabetes_service, get_heart_service, get_stroke_service

def render_page():
    st.title("🩺 Full Health Checkup")
    st.write("Isi data kesehatan lengkap Anda untuk mendapatkan prediksi risiko Diabetes, Penyakit Jantung, dan Stroke.")

    # Instantiate Services
    diabetes_service = get_diabetes_service()
    heart_service = get_heart_service()
    stroke_service = get_stroke_service()

    # --- Form Input Section ---
    # We will use tabs or expanders to organize the many inputs.
    # Grouping based on the original web app logic.
    
    with st.expander("📝 Data Diri & Gaya Hidup", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Umur", min_value=1, max_value=120, value=30)
            sex = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            marital = st.selectbox("Status Pernikahan", ["Belum Menikah", "Menikah"])
            work = st.selectbox("Tipe Pekerjaan", ["Private", "Self-employed", "Govt_job", "Children", "Never_worked"])
        with c2:
            residence = st.selectbox("Tipe Tempat Tinggal", ["Urban", "Rural"])
            smoke = st.selectbox("Status Merokok", ["formerly smoked", "never smoked", "smokes", "Unknown"])
    
    with st.expander("🏥 Indikator Medis Umum", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            bmi = st.number_input("BMI", 10.0, 50.0, 25.0)
            glucose = st.number_input("Rata-rata Gula Darah", 50.0, 300.0, 100.0)
        with c2:
            hypertension = st.checkbox("Riwayat Hipertensi?")
            heart_disease = st.checkbox("Riwayat Penyakit Jantung?")
        with c3:
            bp = st.number_input("Tekanan Darah (Trestbps)", 80, 200, 120)

    with st.expander("❤️ Spesifik Jantung (Heart Disease)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
             cp = st.selectbox("Tipe Nyeri Dada (CP)", [0, 1, 2, 3], format_func=lambda x: f"Tipe {x}")
             chol = st.number_input("Kolesterol (mg/dl)", 100, 600, 200)
             fbs = st.selectbox("Gula Darah Puasa > 120 mg/dl?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
             restecg = st.selectbox("Resting ECG", [0, 1, 2])
        with c2:
             thalach = st.number_input("Detak Jantung Maksimum", 60, 220, 150)
             exang = st.selectbox("Angina Akibat Olahraga?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
             oldpeak = st.number_input("ST Depression (Oldpeak)", 0.0, 10.0, 1.0)
             slope = st.selectbox("Slope ST Segment", [0, 1, 2])
             ca = st.selectbox("Jumlah Pembuluh Utama (CA)", [0, 1, 2, 3])
             thal = st.selectbox("Thalassemia", [0, 1, 2, 3])

    # --- Submission ---
    if st.button("Analisis Kesehatan Lengkap", type="primary"):
        with st.spinner("Memproses data di semua model..."):
            
            # Prepare Data Dictionary
            # Mapping string inputs to values expected by backend logic
            # Sex: Male=1, Female=0 (Usually. Verify with service logic if needed. Stroke uses 1=Male)
            sex_val = 1 if sex == "Laki-laki" else 0
            
            # Simple manual mapping for display -> value
            # This logic mimics the original frontend -> backend payload construction
            
            data_payload = {
                "age": age,
                "sex": sex_val,
                "bmi": bmi,
                "glucose": glucose,
                "bloodpressure": bp,
                
                # Stroke specific
                "hypertension": 1 if hypertension else 0,
                "heartdisease": 1 if heart_disease else 0,
                "maritalstatus": 1 if marital == "Menikah" else 0,
                "worktype": work_map(work),
                "residence": 1 if residence == "Urban" else 0,
                "smoke": smoke_map(smoke),
                
                # Heart specific
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
            
            # Call Services
            # In a real async environment we'd do this in parallel. 
            # In Streamlit sync execution, we call sequentially (fast enough).
            
            res_diabetes = diabetes_service.predict(data_payload)
            res_heart = heart_service.predict(data_payload)
            res_stroke = stroke_service.predict(data_payload)
            
            # --- Display Results ---
            st.markdown("---")
            st.subheader("📊 Hasil Analisis")
            
            t1, t2, t3 = st.tabs(["Diabetes", "Jantung", "Stroke"])
            
            with t1:
                display_result_card("Diabetes", res_diabetes, "diabetes")
            
            with t2:
                display_result_card("Penyakit Jantung", res_heart, "heartd")
            
            with t3:
                display_result_card("Stroke", res_stroke, "stroke")
    
    st.button("Kembali ke Beranda", on_click=lambda: st.session_state.update({"page": "Home"}))

def work_map(w):
    # Mapping 'Private', 'Self-employed', 'Govt_job', 'Children', 'Never_worked'
    # To backend expected integers or strings.
    # Service 'get_mapped_value' usually handles strings if passed key.
    # We'll pass the backend key format if possible.
    mapping = {
        "Private": "privatejob", 
        "Self-employed": "selfemp", 
        "Govt_job": "govtemp", 
        "Children": "children", 
        "Never_worked": "never_worked" # Check dataset for specific key
    }
    return mapping.get(w, "privatejob")

def smoke_map(s):
    # 'formerly smoked', 'never smoked', 'smokes', 'Unknown'
    # Service expects: 'formerly_smoked', 'non_smoker', 'smoker' ?
    # Let's clean spaces.
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
    if "tidak" in prediction_text.lower():
        st.success(f"✅ {prediction_text}")
    else:
        st.error(f"⚠️ {prediction_text}")
        
    with st.expander("Saran & Pencegahan"):
        st.write(res.get(adv_key, "-"))
        
    with st.expander("Faktor Risiko Terkait"):
        st.write(res.get(risk_key, "-"))
