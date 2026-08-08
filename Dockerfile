# ---------- Etapa 1: builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Dependencias de compilación necesarias para scikit-learn/numpy/pandas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---------- Etapa 2: runtime ----------
FROM python:3.11-slim

WORKDIR /app

# Copiar solo los paquetes instalados (sin build tools)
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copiar código y datos necesarios
COPY app/ ./app/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY static/ ./static/
COPY templates/ ./templates/
COPY data/tmdb_5000_movies.csv ./data/tmdb_5000_movies.csv
COPY data/tmdb_5000_credits.csv ./data/tmdb_5000_credits.csv
COPY run.py .

# Generar la base de datos en build time (inmutabilidad)
RUN python scripts/database_setup.py

# Variables de entorno (TMDB_API_KEY se pasa en runtime con -e o --env-file)
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "run.py"]
