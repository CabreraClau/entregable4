# Etapa 1 — Builder
FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Etapa final
FROM python:3.10-slim

WORKDIR /app

# Copiar dependencias del builder
COPY --from=builder /install /usr/local

# Copiar el código
COPY app.py .

# Crear usuario no root (ANTES del chown)
RUN useradd -m appuser

# Crear carpeta de datos y asignar permisos al usuario
RUN mkdir -p /data && chown -R appuser:appuser /data

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
