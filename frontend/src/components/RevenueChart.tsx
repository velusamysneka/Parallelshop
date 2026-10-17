import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Persona, PersonaStats } from "../types";
import { PERSONAS, PERSONA_META, formatINR } from "../format";

export default function RevenueChart({ breakdown }: { breakdown: Partial<Record<Persona, PersonaStats>> }) {
  const data = PERSONAS.filter((p) => breakdown[p]).map((p) => ({
    name: PERSONA_META[p].label.replace(" Shoppers", ""),
    Before: breakdown[p]!.revenue_before,
    After: breakdown[p]!.revenue_after,
  }));
  if (!data.length) return <p className="muted">No persona data returned.</p>;

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a3245" vertical={false} />
        <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
        <YAxis tickFormatter={(v: number) => `₹${(v / 1000).toFixed(0)}k`} tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
        <Tooltip
          formatter={(v: number) => formatINR(v)}
          contentStyle={{ background: "#151b2b", border: "1px solid #2a3245", borderRadius: 8 }}
          cursor={{ fill: "rgba(148,163,184,0.08)" }}
        />
        <Legend wrapperStyle={{ color: "#94a3b8" }} />
        <Bar dataKey="Before" fill="#475569" radius={[4, 4, 0, 0]} />
        <Bar dataKey="After" fill="#6366f1" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
