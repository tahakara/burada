# Python tabanlı imaj (örnek: Python 3.11 slim)
FROM python:3.11-slim

# Ortam değişkenleri (opsiyonel ama tavsiye edilir)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Istanbul

# Çalışma dizini oluştur ve ayarla
WORKDIR /app

# Requirements dosyasını kopyala
COPY ./requirements.txt .

# Python bağımlılıklarını yükle
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Varsayılan komut (docker-compose zaten bunu override ediyor)
CMD ["python", "app.py"]
