import os
import psycopg
from flask import Flask, jsonify, request
from flask_cors import CORS  # Importação corrigida

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://itbi-fen.onrender.com"}})  # Permite requisições do frontend

# Conexão com o banco PostgreSQL remoto
DB_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    try:
        conn = psycopg.connect(DB_URL, autocommit=True)
        print("Conexão com BD bem-sucedida")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

conn = get_db_connection()

@app.route("/")
def home():
    return jsonify({"message": "API ITBI Online"})

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
        print(f"Erro na query de clientes: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/transacoes/<id>", methods=["GET"])
def transacoes(id):
    if conn is None:
        return jsonify({"error": "Sem conexão com o banco"}), 500

    try:
        numero = request.args.get("numero")

        # Normaliza inputs
        id_str = str(id).strip() if id else None
        numero_str = str(numero).strip() if numero else None

        # Usa LIKE para comparar os 6 primeiros dígitos do campo "sql"
        # CAST garante que o campo seja tratado como texto
        query = """
            SELECT "sql", logradouro, numero, cep, valor_transacao, data_transacao, complemento
            FROM transacoes_opt
            WHERE CAST("sql" AS TEXT) LIKE %s
        """

        params = [f"{id_str}%"]

        # Se também vier número, adiciona no filtro
        if numero_str:
            query += " AND CAST(numero AS TEXT) = %s"
            params.append(numero_str)

        query += " ORDER BY data_transacao DESC LIMIT 200"

        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            rows = cur.fetchall()

            if not rows:
                return jsonify({"error": "Transação não encontrada"}), 404

            columns = [desc.name for desc in cur.description]
            data = [dict(zip(columns, row)) for row in rows]

            return jsonify({
                "filtros": {"id": id_str, "numero": numero_str},
                "quantidade": len(data),
                "transacoes": data
            })

    except Exception as e:
        print(f"Erro na query de transações: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
