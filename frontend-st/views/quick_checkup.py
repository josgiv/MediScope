import streamlit as st
from services.checkup_services import get_quick_checkup_service

def render_page():
    st.title("⚡ Quick Checkup")
    st.markdown("Pilih gejala yang Anda rasakan untuk mendapatkan prediksi awal.")

    # Instantiate Service
    checkup = get_quick_checkup_service()

    if not checkup.model:
        st.error("Model Quick Checkup tidak dapat dimuat. Periksa backend/assets.")
        return

    # --- Symptom Selection ---
    available_symptoms = [""] + list(checkup.symptom_weights.keys())
    available_symptoms.sort()

    col1, col2 = st.columns(2)

    with col1:
        s1 = st.selectbox("Gejala 1", available_symptoms, key="s1")
        s2 = st.selectbox("Gejala 2", available_symptoms, key="s2")

    with col2:
        s3 = st.selectbox("Gejala 3", available_symptoms, key="s3")
        s4 = st.selectbox("Gejala 4", available_symptoms, key="s4")

    # --- Prediction Logic ---
    if st.button("Analisa Gejala", type="primary"):
        selected = [s for s in [s1, s2, s3, s4] if s != ""]

        if not selected:
            st.warning("Harap pilih setidaknya satu gejala.")
        else:
            with st.spinner("Menganalisa gejala..."):
                result = checkup.predict(selected)

                # --- Result Display ---
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.markdown("---")
                    st.success("Analisa Selesai!")

                    st.subheader(f"Prediksi: {result['Disease']}")

                    with st.expander("Deskripsi Penyakit", expanded=True):
                        st.write(result["Description"])

                    st.subheader("Saran Pencegahan:")
                    precautions = result["Precautions"]
                    if isinstance(precautions, list):
                        for p in precautions:
                            st.write(f"- {p.title()}")
                    else:
                        st.write(str(precautions))

    st.markdown("---")
    st.info("Catatan: Hasil ini dibuat berdasarkan model Machine Learning dan bobot gejala. Bukan diagnosis pastis.")
    st.button("Kembali ke Beranda", on_click=lambda: st.session_state.update({"page": "Home"}))
