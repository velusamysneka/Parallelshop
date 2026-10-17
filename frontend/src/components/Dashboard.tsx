import type { RunMeta } from "../App";
import type { Scenario, SimulationResult } from "../types";
import { deltaClass, formatINR, formatPct } from "../format";
import RevenueChart from "./RevenueChart";
import ChurnGauge from "./ChurnGauge";
import SubstitutionTable from "./SubstitutionTable";
import CustomerVoices from "./CustomerVoices";
import SegmentComparison from "./SegmentComparison";

interface Props {
  result: SimulationResult;
  run: RunMeta;
  onBack: () => void;
  onRerunLive: () => void;
}

function ScenarioChips({ scenario }: { scenario: Scenario }) {
  const chips = [
    ...(scenario.price_changes ?? []).map((c) => ({
      kind: c.price_delta >= 0 ? "up" : "down",
      text: `${c.product_name} ${c.price_delta >= 0 ? "+" : "−"}₹${Math.abs(c.price_delta)}`,
    })),
    ...(scenario.removed_products ?? []).map((r) => ({ kind: "removed", text: `Removed: ${r.product_name}` })),
    ...(scenario.discount_promotions ?? []).map((d) => ({ kind: "down", text: `${d.discount_pct}% off ${d.target}` })),
  ];
  if (!chips.length) return <span className="muted">No concrete store change detected - try rephrasing the scenario.</span>;
  return (
    <div className="chips">
      {chips.map((c) => <span key={c.text} className={`chip static ${c.kind}`}>{c.text}</span>)}
    </div>
  );
}

export default function Dashboard({ result, run, onBack, onRerunLive }: Props) {
  const m = result.metrics;
  const scenario = result.scenario ?? run.request.scenario_override ?? {};

  return (
    <div className="dashboard">
      <section className="dash-header">
        <div>
          <span className={`badge ${run.source === "cached" ? "cached" : "live"}`}>
            {run.source === "cached" ? "Pre-simulated snapshot" : "Live simulation"}
          </span>
          <h1>{run.label}</h1>
          <ScenarioChips scenario={scenario} />
        </div>
        <div className="dash-actions">
          <button onClick={onBack}>← New scenario</button>
          <button className="primary" onClick={onRerunLive}>Re-run live</button>
        </div>
      </section>

      <section className="kpis">
        <div className="card kpi">
          <span className="muted">Revenue impact</span>
          <strong className={deltaClass(m.revenue_delta_pct)}>{formatPct(m.revenue_delta_pct, true)}</strong>
          <span className="muted">{formatINR(m.baseline_revenue)} → {formatINR(m.simulated_revenue)}</span>
        </div>
        <div className="card kpi">
          <span className="muted">Shoppers who walked out</span>
          <strong className={m.churn_count > 0 ? "neg" : "pos"}>{m.churn_count}</strong>
          <span className="muted">of {m.total_shoppers_simulated} simulated agents</span>
        </div>
        <div className="card kpi">
          <span className="muted">Avg basket size</span>
          <strong>{m.baseline_avg_basket} → {m.simulated_avg_basket}</strong>
          <span className="muted">items per buying shopper</span>
        </div>
        <div className="card kpi">
          <span className="muted">Revenue delta</span>
          <strong className={deltaClass(m.revenue_delta)}>{m.revenue_delta >= 0 ? "+" : ""}{formatINR(m.revenue_delta)}</strong>
          <span className="muted">across the simulated cohort</span>
        </div>
      </section>

      <section className="grid-2">
        <div className="card">
          <h3>Revenue before vs after, by persona</h3>
          <RevenueChart breakdown={result.persona_breakdown} />
        </div>
        <div className="card">
          <h3>Churn risk</h3>
          <ChurnGauge value={m.churn_rate_pct} />
        </div>
      </section>

      <section className="card">
        <h3>Segment comparison - same change, different shoppers</h3>
        <SegmentComparison breakdown={result.persona_breakdown} />
      </section>

      <section className="grid-2">
        <div className="card">
          <h3>Where demand moved</h3>
          <SubstitutionTable flows={result.substitution_flows ?? []} />
        </div>
        <div className="card">
          <h3>Customer voices</h3>
          <CustomerVoices voices={result.customer_voices ?? []} />
        </div>
      </section>
    </div>
  );
}
