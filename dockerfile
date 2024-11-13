# Gunakan image Python yang sesuai dan ringan
FROM python:3.12.7-slim-bullseye

# Menambahkan metadata image
LABEL maintainer="Josia Given Santoso"
LABEL description="MediScope Full Check-Up and Quick Check-Up Application"

# Atur work directory dalam container
WORKDIR /app

# Optimalkan cache layer untuk dependencies OS dan Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-distutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade setuptools dan ensurepip
RUN python -m ensurepip --upgrade && pip install --no-cache-dir --upgrade setuptools

# Salin dan instal requirements dalam satu layer agar cache efektif
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file aplikasi ke dalam direktori kerja container
COPY . .

# Expose port untuk setiap service
EXPOSE 5000 5001 5002 5003 5004 5009 5010

# Tentukan command untuk menjalankan aplikasi
CMD ["python", "main.py"]
