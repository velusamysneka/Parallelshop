import { useEffect, useState } from "react";
import { PERSONAS, PERSONA_META } from "../format";

interface Props {
  label: string;
  expectedShoppers: number;
  done: boolean;
}

const STAGES = [
  { at: 0, text: "Parsing scenario into structured store changes with Gemini…" },
  { at: 0.12, text: "Loading 4 persona cohorts and purchase histories from BigQuery…" },
  { at: 0.25, text: "Simulating shopper agents in parallel…" },
  { at: 0.85, text: "Aggregating revenue, churn and substitution flows…" },
];

export default function LoadingView({ label, expectedShoppers, done }: Props) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const start = Date.now();
    const id = setInterval(() => setElapsed(Date.now() - start), 80);
    return () => clearInterval(id);
  }, []);

  // Eases toward ~95% while waiting on the API; snaps to 100% once the result is in.
  const progress = done ? 1 : 0.95 * (1 - Math.exp(-elapsed / 2500));
  const simulated = Math.round(expectedShoppers * Math.min(1, Math.max(0, (progress - 0.25) / 0.6)));
  const stageIdx = STAGES.reduce((acc, s, i) => (progress >= s.at ? i : acc), 0);

  return (
    <div className="loading-screen card">
      <div className="pulse-ring" />
      <h2>Simulating: <span className="accent">{label}</span></h2>
      <div className="progress"><div style={{ width: `${progress * 100}%` }} /></div>
      <ul className="stages">
        {STAGES.map((s, i) => (
          <li key={s.text} className={i < stageIdx || done ? "done" : i === stageIdx ? "current" : ""}>
            {s.text}
            {i === 2 && i <= stageIdx && <strong> {simulated} / {expectedShoppers} shoppers</strong>}
          </li>
        ))}
      </ul>
      <div className="persona-dots">
        {PERSONAS.map((p, i) => (
          <span key={p} className="persona-dot" style={{ background: PERSONA_META[p].color, animationDelay: `${i * 0.15}s` }}>
            {PERSONA_META[p].label}
          </span>
        ))}
      </div>
    </div>
  );
}
