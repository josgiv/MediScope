# Gunakan image Python yang sesuai
FROM python:3.12.7-slim-bullseye

# Menambahkan metadata image
LABEL maintainer="Josia Given Santoso"
LABEL description="MediScope Full Check-Up and Quick Check-Up Application"

# Atur work directory dalam container
WORKDIR /app

# Instal distutils untuk mengatasi error 'No module named distutils'
RUN apt-get update && apt-get install -y python3-distutils

# Salin semua file ke dalam direktori kerja container
COPY . .

RUN pip install --upgrade setuptools

RUN python -m ensurepip --upgrade

# Install dependencies dari requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
EXPOSE 5001
EXPOSE 5002
EXPOSE 5003
EXPOSE 5004
EXPOSE 5009
EXPOSE 5010

CMD ["python", "main.py"]
