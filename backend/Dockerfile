FROM python:3.11-slim

# no generar basuras .pyc y se muestren los logs rapidamente pues
ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libheif1 \
    libjpeg62-turbo \
    zlib1g \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# instalacion de dependencias 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8003

# si le muevo a algo no tengo que recargar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
