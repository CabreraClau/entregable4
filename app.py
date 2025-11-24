from flask import Flask, jsonify, request
import os

app = Flask(__name__)

DATA_PATH = "/data"
NOTES_FILE = f"{DATA_PATH}/notas.txt"

# Crear almacenamiento persistente
os.makedirs(DATA_PATH, exist_ok=True)
if not os.path.exists(NOTES_FILE):
    open(NOTES_FILE, "w").close()

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
