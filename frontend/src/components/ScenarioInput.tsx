import { useState } from "react";
import type { Preset } from "../types";
import { PERSONAS, PERSONA_META } from "../format";

interface Props {
  presets: Preset[];
  cachedIds: Set<string>;
  apiOffline: boolean;
  error: string | null;
  onRunPrompt: (prompt: string, quickMode: boolean, sampleSize: number) => void;
  onRunPreset: (preset: Preset, sampleSize: number) => void;
}

const EXAMPLES = [
  "Raise milk price by ₹5",
  "Remove white bread from the shelves",
  "Hike basmati rice by ₹40",
];

export default function ScenarioInput({ presets, cachedIds, apiOffline, error, onRunPrompt, onRunPreset }: Props) {
  const [prompt, setPrompt] = useState("");
  const [quickMode, setQuickMode] = useState(true);
  const [sampleSize, setSampleSize] = useState(15);

  const submit = () => prompt.trim() && onRunPrompt(prompt.trim(), quickMode, sampleSize);
  const shoppers = quickMode ? 20 : sampleSize * 4;

  return (
    <div className="input-screen">
      <section className="hero">
        <h1>What if you changed your store tomorrow?</h1>
        <p>
          Describe a pricing, assortment or promo decision. ParallelShop replays it on a population of Gemini shopper agents,
          each grounded in a real customer's purchase history, and shows what happens before you roll it out.
        </p>
      </section>

      <section className="card scenario-box">
        <label htmlFor="prompt">Your what-if scenario</label>
        <textarea
          id="prompt"
          value={prompt}
          placeholder='e.g. "Raise Fresh Milk price by ₹2 and remove Organic Bananas"'
          rows={3}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && (e.metaKey || e.ctrlKey) && submit()}
        />
        <div className="examples">
          {EXAMPLES.map((ex) => (
            <button key={ex} className="chip" onClick={() => setPrompt(ex)}>{ex}</button>
          ))}
        </div>
        <div className="scenario-actions">
          <label className="toggle">
            <input type="checkbox" checked={quickMode} onChange={(e) => setQuickMode(e.target.checked)} />
            Quick mode
          </label>
          {!quickMode && (
            <label className="slider">
              Shoppers per persona: <strong>{sampleSize}</strong>
              <input type="range" min={5} max={50} step={5} value={sampleSize} onChange={(e) => setSampleSize(+e.target.value)} />
            </label>
          )}
          <span className="muted">{shoppers} shopper agents</span>
          <button className="primary" disabled={!prompt.trim() || apiOffline} onClick={submit}>
            Run simulation
          </button>
        </div>
        {apiOffline && <p className="warn">Simulation API is unreachable. Cached presets below still work.</p>}
        {error && <p className="error">Simulation failed: {error}</p>}
      </section>

      <section>
        <h2 className="section-title">Demo scenarios</h2>
        <div className="preset-grid">
          {presets.map((p) => {
            const cached = cachedIds.has(p.id);
            return (
              <button
                key={p.id}
                className="card preset"
                disabled={!cached && apiOffline}
                onClick={() => onRunPreset(p, sampleSize)}
              >
                <span className={`badge ${cached ? "cached" : ""}`}>{cached ? "Instant · pre-simulated" : "Live run"}</span>
                <strong>{p.title}</strong>
                <span className="muted">{p.prompt}</span>
              </button>
            );
          })}
        </div>
      </section>

      <section>
        <h2 className="section-title">Who's in the simulated store</h2>
        <div className="persona-grid">
          {PERSONAS.map((p) => (
            <div key={p} className="persona-card" style={{ borderColor: PERSONA_META[p].color }}>
              <strong style={{ color: PERSONA_META[p].color }}>{PERSONA_META[p].label}</strong>
              <span className="muted">{PERSONA_META[p].blurb}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
