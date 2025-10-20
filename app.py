import React, { useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://itbi-bke.onrender.com';

function App() {
  const [sqlPrefix, setSqlPrefix] = useState("");
  const [numero, setNumero] = useState("");
  const [transacoes, setTransacoes] = useState([]);
  const [selectedTransacoes, setSelectedTransacoes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null); // Novo estado para erros

  const handleSearch = async () => {
    if (!sqlPrefix) return;

    setLoading(true);
    setError(null); // Limpa erro anterior
    try {
      const response = await axios.get(
        `${API_BASE_URL}/transacoes/${sqlPrefix}`,
        {
          params: numero ? { numero } : {},
        }
      );
      const data = response.data.transacoes || [];
      setTransacoes(data);
      setSelectedTransacoes(data.map((t) => t.sql));
      console.log("✅ Resposta backend:", response.data);
    } catch (error) {
      console.error("Erro ao buscar transações:", error);
      setTransacoes([]);
      setSelectedTransacoes([]);
      // Define mensagem de erro específica para 404
      if (error.response && error.response.status === 404) {
        setError("Nenhuma transação encontrada para os filtros fornecidos.");
      } else {
        setError("Erro ao buscar transações. Tente novamente.");
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleTransaction = (sql) => {
    if (selectedTransacoes.includes(sql)) {
      setSelectedTransacoes(selectedTransacoes.filter((s) => s !== sql));
    } else {
      setSelectedTransacoes([...selectedTransacoes, sql]);
    }
  };

  const filteredTransacoes = transacoes.filter((t) =>
    selectedTransacoes.includes(t.sql)
  );

  const sortedTransacoes = [...filteredTransacoes].sort(
    (a, b) => new Date(a.data_transacao) - new Date(b.data_transacao)
  );

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Transações ITBI - PMSP</h1>

      <div className="mb-4 flex gap-2">
        <input
          type="text"
          placeholder="Prefixo SQL (6 dígitos)"
          value={sqlPrefix}
          onChange={(e) => setSqlPrefix(e.target.value)}
          className="border p-2 rounded"
        />
        <input
          type="number"
          placeholder="Número do imóvel (opcional)"
          value={numero}
          onChange={(e) => setNumero(e.target.value)}
          className="border p-2 rounded"
        />
        <button
          onClick={handleSearch}
          className="bg-purple-500 text-white p-2 rounded"
        >
          Buscar
        </button>
      </div>

      {loading && <p>Carregando transações...</p>}
      {error && <p className="text-red-500">{error}</p>} {/* Exibe erro */}

      {transacoes.length > 0 ? (
        <>
          <h2 className="text-xl font-bold mt-6 mb-2">Gráfico de Transações</h2>
          <div className="mb-4">
            {transacoes.map((t) => (
              <label key={t.sql} className="mr-4">
                <input
                  type="checkbox"
                  checked={selectedTransacoes.includes(t.sql)}
                  onChange={() => toggleTransaction(t.sql)}
                />
                {` ${t.sql}`}
              </label>
            ))}
          </div>

          <BarChart
            width={800}
            height={300}
            data={sortedTransacoes}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="data_transacao"
              tickFormatter={(tick) =>
                new Date(tick).toLocaleDateString("pt-BR")
              }
            />
            <YAxis />
            <Tooltip
              formatter={(value) =>
                value.toLocaleString("pt-BR", {
                  style: "currency",
                  currency: "BRL",
                })
              }
            />
            <Legend />
            <Bar
              dataKey="valor_transacao"
              fill="#7e57c2"
              name="Valor da transação"
            />
          </BarChart>

          <h2 className="text-xl font-bold mt-6 mb-2">Lista de Transações</h2>
          <table className="table-auto border-collapse border border-gray-400 w-full">
            <thead>
              <tr>
                <th className="border p-2">SQL</th>
                <th className="border p-2">Logradouro</th>
                <th className="border p-2">Número</th>
                <th className="border p-2">Complemento</th>
                <th className="border p
