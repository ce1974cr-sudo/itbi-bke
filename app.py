@app.route("/transacoes/<id>", methods=["GET"])
def transacoes(id):
    if conn is None:
        return jsonify({"error": "Sem conexão com o banco"}), 500
    try:
        numero = request.args.get("numero")  # Pega ?numero=325
        with conn.cursor() as cur:
            # Ajusta a query para usar AND quando numero é fornecido
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
