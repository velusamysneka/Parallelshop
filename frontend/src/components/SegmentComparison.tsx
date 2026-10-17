import { useState } from "react";
import type { Persona, PersonaStats } from "../types";
import { PERSONA_META, deltaClass, formatINR, formatPct, PERSONAS } from "../format";

type Breakdown = Partial<Record<Persona, PersonaStats>>;

function SegmentCard({ persona, stats }: { persona: Persona; stats: PersonaStats }) {
  const meta = PERSONA_META[persona];
  return (
    <div className="segment-card" style={{ borderColor: meta.color }}>
      <strong style={{ color: meta.color }}>{meta.label}</strong>
      <div className={`big ${deltaClass(stats.revenue_delta_pct)}`}>{formatPct(stats.revenue_delta_pct, true)}</div>
      <span className="muted">revenue · {formatINR(stats.revenue_before)} → {formatINR(stats.revenue_after)}</span>
      <div className="segment-row">
        <span>Churn <strong className={stats.churn_rate > 0 ? "neg" : ""}>{formatPct(stats.churn_rate)}</strong></span>
        <span>Shoppers <strong>{stats.shopper_count}</strong></span>
      </div>
    </div>
  );
}

export default function SegmentComparison({ breakdown }: { breakdown: Breakdown }) {
  const available = PERSONAS.filter((p) => breakdown[p]);
  // Default to the two most divergent segments - that's the demo moment.
  const sorted = [...available].sort((x, y) => breakdown[y]!.revenue_delta_pct - breakdown[x]!.revenue_delta_pct);
  const [a, setA] = useState<Persona | undefined>(sorted[0]);
  const [b, setB] = useState<Persona | undefined>(sorted[sorted.length - 1]);

  if (available.length < 2 || !a || !b) return <p className="muted">Need at least two segments to compare.</p>;

  const sa = breakdown[a]!;
  const sb = breakdown[b]!;
  const opposite = Math.sign(sa.revenue_delta_pct) !== Math.sign(sb.revenue_delta_pct);
  const gap = Math.abs(sa.revenue_delta_pct - sb.revenue_delta_pct).toFixed(1);

  const picker = (value: Persona, onChange: (p: Persona) => void) => (
    <select value={value} onChange={(e) => onChange(e.target.value as Persona)}>
      {available.map((p) => <option key={p} value={p}>{PERSONA_META[p].label}</option>)}
    </select>
  );

  return (
    <div className="segments">
      <div className="segment-pickers">
        {picker(a, setA)}
        <span className="muted">vs</span>
        {picker(b, setB)}
      </div>
      <div className="segment-pair">
        <SegmentCard persona={a} stats={sa} />
        <SegmentCard persona={b} stats={sb} />
      </div>
      <p className={`verdict ${opposite ? "highlight" : ""}`}>
        {opposite
          ? `Opposite outcomes: the same decision moves ${PERSONA_META[a].label} and ${PERSONA_META[b].label} in different directions (${gap} pt gap). A one-size-fits-all rollout would hide this.`
          : `${gap} pt revenue gap between ${PERSONA_META[a].label} and ${PERSONA_META[b].label} under the same change.`}
      </p>
    </div>
  );
}
