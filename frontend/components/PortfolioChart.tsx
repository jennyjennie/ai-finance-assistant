"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const PERIODS = ["1mo", "3mo", "6mo", "1y", "2y"] as const;
type Period = (typeof PERIODS)[number];

const COLORS = ["#0070f3", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#ec4899"];

type Holding = { symbol: string; weight: string };

export default function PortfolioChart() {
  const [holdings, setHoldings] = useState<Holding[]>([
    { symbol: "AAPL", weight: "30" },
    { symbol: "NVDA", weight: "40" },
    { symbol: "MSFT", weight: "30" },
  ]);
  const [period, setPeriod] = useState<Period>("1y");
  const [chartData, setChartData] = useState<Record<string, string | number>[]>([]);
  const [symbols, setSymbols] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function addHolding() {
    setHoldings([...holdings, { symbol: "", weight: "" }]);
  }

  function removeHolding(i: number) {
    setHoldings(holdings.filter((_, idx) => idx !== i));
  }

  function updateHolding(i: number, field: keyof Holding, value: string) {
    const updated = [...holdings];
    updated[i] = { ...updated[i], [field]: value.toUpperCase() };
    setHoldings(updated);
  }

  async function fetchChart() {
    setError("");
    const valid = holdings.filter((h) => h.symbol && h.weight);
    if (valid.length < 1) {
      setError("Enter at least one holding.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/portfolio/history`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            holdings: valid.map((h) => ({ symbol: h.symbol, weight: parseFloat(h.weight) })),
            period,
          }),
        }
      );
      if (!res.ok) {
        const err = await res.json();
        setError(err.detail ?? "Request failed");
        return;
      }
      const json = await res.json();
      setChartData(json.data);
      setSymbols(json.symbols);
    } catch {
      setError("Could not reach server.");
    } finally {
      setLoading(false);
    }
  }

  const lines = chartData.length > 0 ? ["Portfolio", ...symbols] : [];

  return (
    <div style={{ padding: "20px 16px", maxWidth: 800, margin: "0 auto" }}>
      {/* Description */}
      <div style={{ marginBottom: 16 }}>
        <p style={{ margin: "0 0 4px", fontWeight: 600, fontSize: 15 }}>Portfolio Performance Chart</p>
        <p style={{ margin: 0, fontSize: 13, color: "#888", lineHeight: 1.5 }}>
          Enter your holdings and weights to visualize historical performance. Each asset is normalized to 100 at the start date so you can compare returns side by side.
        </p>
      </div>

      {/* Holdings input */}
      <div style={{ background: "#fff", borderRadius: 12, padding: 16, boxShadow: "0 1px 3px rgba(0,0,0,0.1)", marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <span style={{ fontWeight: 600, fontSize: 15 }}>Holdings</span>
          <div style={{ display: "flex", gap: 8 }}>
            {PERIODS.map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                style={{
                  padding: "4px 10px",
                  borderRadius: 6,
                  border: "1px solid #ddd",
                  background: period === p ? "#0070f3" : "#fff",
                  color: period === p ? "#fff" : "#333",
                  cursor: "pointer",
                  fontSize: 13,
                }}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {holdings.map((h, i) => (
          <div key={i} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            <input
              value={h.symbol}
              onChange={(e) => updateHolding(i, "symbol", e.target.value)}
              placeholder="Symbol (e.g. AAPL)"
              style={{ flex: 2, padding: "8px 10px", borderRadius: 6, border: "1px solid #ddd", fontSize: 14 }}
            />
            <div style={{ flex: 1, display: "flex", alignItems: "center", border: "1px solid #ddd", borderRadius: 6, overflow: "hidden" }}>
              <input
                value={h.weight}
                onChange={(e) => updateHolding(i, "weight", e.target.value)}
                placeholder="%"
                type="number"
                style={{ flex: 1, padding: "8px 10px", border: "none", fontSize: 14, outline: "none", minWidth: 0 }}
              />
              <span style={{ padding: "0 10px", color: "#888", fontSize: 14, background: "#f5f5f5", alignSelf: "stretch", display: "flex", alignItems: "center", borderLeft: "1px solid #ddd" }}>%</span>
            </div>
            <button
              onClick={() => removeHolding(i)}
              disabled={holdings.length === 1}
              style={{
                padding: "8px 12px", borderRadius: 6, border: "1px solid #ddd",
                background: "#fff", cursor: "pointer", color: "#888", fontSize: 16,
              }}
            >
              ×
            </button>
          </div>
        ))}

        <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
          <button
            onClick={addHolding}
            style={{ padding: "8px 14px", borderRadius: 6, border: "1px dashed #aaa", background: "#fafafa", cursor: "pointer", fontSize: 13, color: "#555" }}
          >
            + Add Stock
          </button>
          <button
            onClick={fetchChart}
            disabled={loading}
            style={{ padding: "8px 20px", borderRadius: 6, border: "none", background: "#0070f3", color: "#fff", cursor: "pointer", fontSize: 14, opacity: loading ? 0.6 : 1 }}
          >
            {loading ? "Loading…" : "Generate Chart"}
          </button>
        </div>
        {error && <p style={{ color: "#ef4444", fontSize: 13, marginTop: 8 }}>{error}</p>}
      </div>

      {/* Chart */}
      {chartData.length > 0 && (
        <div style={{ background: "#fff", borderRadius: 12, padding: 16, boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
          <p style={{ margin: "0 0 12px", fontSize: 13, color: "#666" }}>
            Normalized to 100 at start · {period} period
          </p>
          <ResponsiveContainer width="100%" height={340}>
            <LineChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11 }}
                tickFormatter={(d) => d.slice(5)}
                interval="preserveStartEnd"
              />
              <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
              <Tooltip
                formatter={(value: number, name: string) => [`${value.toFixed(2)}`, name]}
                labelFormatter={(l) => `Date: ${l}`}
              />
              <Legend />
              {lines.map((key, i) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={key === "Portfolio" ? "#111" : COLORS[i % COLORS.length]}
                  strokeWidth={key === "Portfolio" ? 2.5 : 1.5}
                  dot={false}
                  strokeDasharray={key === "Portfolio" ? undefined : "4 2"}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
