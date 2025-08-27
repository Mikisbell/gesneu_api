# Etapa de construcción
FROM python:3.10-slim as builder

WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.5.1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Configurar Poetry
RUN poetry config virtualenvs.create false \
    && poetry config virtualenvs.in-project false

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock* ./

# Instalar dependencias del proyecto
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Etapa final
FROM python:3.10-slim

WORKDIR /usr/src/app

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="${PYTHONPATH}:/usr/src/app"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual desde el builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copiar la aplicación
COPY . .

# Puerto expuesto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "ges_neu_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
