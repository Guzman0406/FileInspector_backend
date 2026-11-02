# ---- Imagen base ----
FROM python:3.11-slim

# ---- Variables de entorno de Python ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---- Dependencias de sistema ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libheif1 \
    libjpeg62-turbo \
    zlib1g \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ---- Directorio de trabajo ----
WORKDIR /app

# ---- Instalación de dependencias Python ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copia del código fuente ----
COPY . .

# ---- Puerto expuesto ----
EXPOSE 8003

# ---- Comando de arranque ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
