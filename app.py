from flask import Flask, jsonify
from flask_cors import CORS
import psycopg
import os

app = Flask(__name__)
CORS(app)

# Conexão com o banco PostgreSQL remoto
DB_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg.connect(DB_URL, autocommit=True)
except Exception as e:
    print("Erro ao conectar ao banco:", e)
    conn = None

@app.route("/")
def home():
    return "API ITBI Online"

@app.route("/clientes")
def clientes():
    if conn is None:
        return jsonify({"error": "Sem conexão com o banco"}), 500
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, endereco FROM clientes LIMIT 10;")
            rows = cur.fetchall()
            data = [{"id": r[0], "nome": r[1], "endereco": r[2]} for r in rows]
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
