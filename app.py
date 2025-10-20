import os
import psycopg
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)  # Definição de 'app' NO INÍCIO, antes de qualquer rota
CORS(app)  # Permite requisições do frontend

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
        numero = request.args.get("numero")  # Pega ?numero=600
        with conn.cursor() as cur:
            # Filtragem corrigida: usa AND para exigir ambos sql e numero
            if numero:
                query = """
                    SELECT sql, logradouro, numero, cep, valor_transacao, data_transacao, complemento
                    FROM transacoes_opt
                    WHERE sql = %s AND numero = %s
                """
                cur.execute(query, (id, numero))
            else:
                query = """
                    SELECT sql, logradouro, numero, cep, valor_transacao, data_transacao, complemento
                    FROM transacoes_opt
                    WHERE sql = %s
                """
                cur.execute(query, (id,))
            rows = cur.fetchall()
            if not rows:
                return jsonify({"error": "Transação não encontrada"}), 404
            columns = [desc.name for desc in cur.description]
            data = [dict(zip(columns, row)) for row in rows]
            return jsonify({
                "id": id,
                "numero": numero,
                "transacoes": data
            })
    except Exception as e:
        print(f"Erro na query de transações: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
