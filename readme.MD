# MediScope: Sistem Deteksi Kesehatan Berbasis AI

MediScope (Medical Scope) adalah sistem prototipe untuk deteksi dini penyakit menggunakan algoritma Machine Learning. Dokumen ini merupakan panduan teknis resmi untuk instalasi dan pengoperasian sistem.

---

## BAB I: Spesifikasi Lingkungan Pengembangan
Untuk menjamin stabilitas eksekusi algoritma Machine Learning dan antarmuka web, lingkungan komputasi wajib memenuhi spesifikasi berikut:

### 1.1 Persyaratan Perangkat Lunak (Software)
*   **Sistem Operasi**: Windows 10/11, macOS, atau Linux (Ubuntu 20.04 LTS ke atas).
*   **Bahasa Pemrograman Python**: Wajib Versi 20.0.0 atau lebih baru (sesuai spesifikasi sistem modern, disarankan 3.10+).
*   **JavaScript Runtime**: Node.js (Versi LTS Terbaru).
*   **Manajemen Paket**:
    *   `pip` (Python Package Installer).
    *   `bun` (JavaScript Package Manager) - Mandatori untuk eksekusi modul frontend Next.js.

---

## BAB II: Instalasi dan Konfigurasi Sistem
Proses instalasi dilakukan melalui terminal (Command Line Interface). Pastikan path sistem untuk Git, Python, dan Bun telah terkonfigurasi dengan benar.

### 2.1 Persiapan Repositori
Salin kode sumber (source code) dari repositori utama ke direktori lokal:
```bash
git clone https://github.com/josgiv/MediScope
cd MediScope
```

### 2.2 Instalasi Dependensi Backend
Instalasi pustaka Python yang diperlukan untuk data processing dan modeling (scikit-learn, pandas, dll) menggunakan berkas `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2.3 Instalasi Dependensi Frontend
Masuk ke direktori antarmuka web dan instal dependensi JavaScript menggunakan `bun`:
```bash
cd web
bun install
cd ..
```
*(Perintah `cd ..` memastikan terminal kembali ke direktori root proyek untuk langkah selanjutnya)*

---

## BAB III: Prosedur Eksekusi Aplikasi
MediScope memiliki dua mode deployment yang dapat dijalankan sesuai kebutuhan pengguna:

### 3.1 Mode Prototyping (Streamlit)
Mode ini digunakan untuk keperluan debugging model atau penggunaan ringan tanpa arsitektur full-stack.

**Perintah Eksekusi:**
```bash
cd frontend_st
streamlit run main_st.py
```
Aplikasi akan berjalan pada port default: [http://localhost:8501](http://localhost:8501)

### 3.2 Mode Aplikasi Web Terintegrasi (Full Stack)
Mode produksi yang mengintegrasikan Backend (Python) dan Frontend (Next.js) dalam satu orkestrasi.

**Perintah Eksekusi:**
Pastikan terminal berada di root folder (direktori utama), lalu jalankan:
```bash
python main.py
```
Aplikasi akan berjalan pada port server web: [http://localhost:3000](http://localhost:3000) (atau port yang tertera di terminal).

---

## BAB IV: Antarmuka dan Panduan Operasional

### 4.1 Halaman Utama (Dashboard)
Saat aplikasi diakses, pengguna akan disajikan halaman Beranda yang memuat:
*   **Navigasi Sidebar**: Menu akses cepat ke Beranda, Quick Checkup, dan Full Checkup.
*   **Panel Informasi**: Judul sistem "MediScope" dan opsi pemilihan mode pemeriksaan kesehatan.

### 4.2 Modul Quick Checkup (Analisis Gejala)
Fitur ini menggunakan inferensi model untuk memprediksi penyakit berdasarkan input gejala kualitatif.

**Langkah Operasional:**
1.  Navigasi ke menu **Quick Checkup**.
2.  Pada formulir yang tersedia, pilih gejala yang dirasakan pada 4 kolom input (Dropdown):
    *   **Gejala 1** (Utama)
    *   **Gejala 2** (Tambahan 1)
    *   **Gejala 3** (Tambahan 2)
    *   **Gejala 4** (Tambahan 3)
3.  Tekan tombol merah **"Analisa Gejala"**.

**Keluaran Sistem:**
Sistem akan menampilkan hasil analisis berupa:
*   **Prediksi**: Identifikasi nama penyakit (Contoh: Psoriasis).
*   **Deskripsi Penyakit**: Definisi medis singkat terkait penyakit yang terdeteksi.
*   **Saran Pencegahan**: Langkah mitigasi preventif (Contoh: Cuci Tangan Dengan Air Hangat, Jaga Berat Badan).
*   *Catatan Teknis: Hasil ini digenerasikan oleh model Machine Learning.*

### 4.3 Modul Full Checkup (Analisis Risiko Komprehensif)
Fitur ini melakukan kalkulasi probabilitas risiko penyakit kronis (Diabetes, Jantung, Stroke) berdasarkan parameter kuantitatif.

**Langkah Operasional:**
1.  Navigasi ke menu **Full Checkup**.
2.  Lengkapi parameter **Data Diri & Gaya Hidup**:
    *   Umur, Jenis Kelamin, Status Pernikahan.
    *   Tipe Pekerjaan, Tipe Tempat Tinggal, Status Merokok.
3.  Lengkapi parameter **Indikator Medis Umum**:
    *   BMI (Body Mass Index).
    *   Rata-rata Gula Darah.
    *   Tekanan Darah (Trestbps).
    *   Riwayat Medis (Hipertensi/Penyakit Jantung).
4.  Klik tombol eksekusi/analisis.

**Keluaran Sistem:**
Laporan yang menyajikan persentase peluang risiko terkena penyakit terkait dan rekomendasi kesehatan spesifik berdasarkan data yang dimasukkan.

---

## BAB V: Penutup
Dokumen ini merupakan panduan teknis resmi untuk instalasi dan pengoperasian sistem MediScope. Seluruh instruksi baris perintah (command line) dan alur kerja fitur telah divalidasi sesuai dengan versi rilis perangkat lunak saat ini.
