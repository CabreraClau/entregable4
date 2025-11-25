from flask import Flask, jsonify, request, Response, g
import os
import time

from prometheus_client import (
    generate_latest, 
    CONTENT_TYPE_LATEST, 
    Counter, 
    Histogram
)

app = Flask(__name__)

DATA_PATH = "/data"
NOTES_FILE = f"{DATA_PATH}/notas.txt"

# Crear almacenamiento persistente
os.makedirs(DATA_PATH, exist_ok=True)
if not os.path.exists(NOTES_FILE):
    open(NOTES_FILE, "w").close()

# ===========================
# MÉTRICAS PROMETHEUS
# ===========================

# Total de requests procesadas
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total de requests recibidas",
    ["endpoint"]
)

# Latencia de requests
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Latencia de requests por endpoint",
    ["endpoint"]
)


@app.before_request
def before_request():
    g.start_time = time.time()


@app.after_request
def after_request(response):
    endpoint = request.path
    REQUEST_COUNT.labels(endpoint=endpoint).inc()
    latency = time.time() - g.start_time
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    return response


# Endpoint /metrics para Prometheus
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# ===========================
# RUTAS NORMALES
# ===========================

@app.get("/")
def home():
    env = os.getenv("APP_ENV", "desconocido")
    return f"""
    <html>
        <head><title>Notas App</title></head>
        <body style="font-family: Arial;">
            <h1>📘 Aplicación de Notas</h1>
            <p>Backend funcionando correctamente.</p>
            <p><b>Entorno actual:</b> {env}</p>
            <hr>
            <p>Endpoints disponibles:</p>
            <ul>
                <li>GET /notas → listar notas</li>
                <li>POST /notas → agregar nota</li>
                <li>GET /env → mostrar entorno actual</li>
                <li>GET /health → healthcheck</li>
                <li>GET /metrics → métricas Prometheus</li>
            </ul>
        </body>
    </html>
    """


@app.get("/notas")
def get_notas():
    with open(NOTES_FILE, "r") as f:
        notas = [n.strip() for n in f.readlines()]
    return jsonify({"notas": notas})


@app.post("/notas")
def add_nota():
    data = request.json
    nota = data.get("nota", None)
    if nota is None:
        return jsonify({"error": "Debe enviar un campo 'nota'"}), 400

    with open(NOTES_FILE, "a") as f:
        f.write(nota + "\n")

    return jsonify({"status": "ok", "agregada": nota})


@app.get("/env")
def environment():
    env = os.getenv("APP_ENV", "desconocido")
    return jsonify({"environment": env})


@app.get("/health")
def health():
    return "OK"


if __name__ == "__main__":
    PORT = int(os.getenv("APP_PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
