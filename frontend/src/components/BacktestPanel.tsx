import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api";
import type { BacktestResult } from "../types";

export default function BacktestPanel({ cached }: { cached: BacktestResult | null }) {
  const [result, setResult] = useState<BacktestResult | null>(cached);
  const [source, setSource] = useState<"cached" | "live">("cached");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runLive() {
    setLoading(true);
    setError(null);
    try {
      setResult(await api.backtest(25));
      setSource("live");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  const data = result?.comparison.map((r) => ({
    name: r.behavior,
    "Actual (hold-out)": r.actual_historical_pct,
    "Predicted (agents)": r.predicted_agent_pct,
  }));

  return (
    <div className="backtest">
      <section className="dash-header">
        <div>
          {result && <span className={`badge ${source === "cached" ? "cached" : "live"}`}>{source === "cached" ? "Pre-computed" : "Live back-test"}</span>}
          <h1>Does the twin match reality?</h1>
          <p className="muted">
            We replay a historical stockout on agents built only from data before the event, then compare their choices
            with what real customers actually did in the hold-out orders.
          </p>
        </div>
        <div className="dash-actions">
          <button className="primary" disabled={loading} onClick={runLive}>{loading ? "Running…" : "Run back-test live"}</button>
        </div>
      </section>

      {error && <p className="error">Back-test failed: {error}</p>}

      {!result ? (
        <div className="card empty">
          <p>No back-test result yet. Click <strong>Run back-test live</strong> to evaluate the agents against hold-out data.</p>
        </div>
      ) : (
        <>
          <section className="card killer-stat">
            <span className="muted">{result.event_name} · {result.shoppers_evaluated} shoppers evaluated</span>
            <strong>{result.killer_slide_stat}</strong>
          </section>

          <section className="grid-2">
            <div className="card">
              <h3>Predicted vs actual behaviour</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2a3245" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} interval={0} />
                  <YAxis unit="%" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <Tooltip formatter={(v: number) => `${v}%`} contentStyle={{ background: "#151b2b", border: "1px solid #2a3245", borderRadius: 8 }} cursor={{ fill: "rgba(148,163,184,0.08)" }} />
                  <Legend wrapperStyle={{ color: "#94a3b8" }} />
                  <Bar dataKey="Actual (hold-out)" fill="#475569" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Predicted (agents)" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <h3>Error by behaviour</h3>
              <table className="flows">
                <thead><tr><th>Behaviour</th><th>Actual</th><th>Predicted</th><th>Abs. error</th></tr></thead>
                <tbody>
                  {result.comparison.map((r) => (
                    <tr key={r.behavior}>
                      <td>{r.behavior}</td>
                      <td>{r.actual_historical_pct}%</td>
                      <td>{r.predicted_agent_pct}%</td>
                      <td>{r.absolute_error_pct} pt</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="mae">Mean absolute error: <strong>{result.mean_absolute_error_pct} pt</strong></p>
              <p className="muted small">{result.methodology}</p>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
