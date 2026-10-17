import { useEffect, useState } from "react";
import { api, API_BASE } from "./api";
import snapshotData from "./data/snapshot.json";
import type { Health, Preset, SimulateRequest, SimulationResult, Snapshot } from "./types";
import ScenarioInput from "./components/ScenarioInput";
import LoadingView from "./components/LoadingView";
import Dashboard from "./components/Dashboard";
import BacktestPanel from "./components/BacktestPanel";

const snapshot = snapshotData as unknown as Snapshot;
const CACHED_PRESET_DELAY_MS = 2400;
const MIN_LIVE_DELAY_MS = 1200;

type View = "input" | "loading" | "results";
type Tab = "simulate" | "credibility";
export type RunSource = "cached" | "live";

export interface RunMeta {
  label: string;
  source: RunSource;
  request: SimulateRequest;
  expectedShoppers: number;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export default function App() {
  const [tab, setTab] = useState<Tab>("simulate");
  const [view, setView] = useState<View>("input");
  const [health, setHealth] = useState<Health | null | "offline">(null);
  const [presets, setPresets] = useState<Preset[]>(snapshot.presets);
  const [run, setRun] = useState<RunMeta | null>(null);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingDone, setLoadingDone] = useState(false);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth("offline"));
    api.presets().then((p) => p.length && setPresets(p)).catch(() => undefined);
  }, []);

  async function execute(meta: RunMeta, fetcher: () => Promise<SimulationResult>, minDelay: number) {
    setRun(meta);
    setError(null);
    setLoadingDone(false);
    setView("loading");
    try {
      const [res] = await Promise.all([fetcher(), sleep(minDelay)]);
      setLoadingDone(true);
      await sleep(400);
      setResult(res);
      setView("results");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setView("input");
    }
  }

  function runLive(label: string, request: SimulateRequest) {
    const perPersona = request.quick_mode ? 5 : request.sample_size_per_persona ?? 15;
    execute(
      { label, source: "live", request, expectedShoppers: perPersona * 4 },
      () => api.simulate(request),
      MIN_LIVE_DELAY_MS,
    );
  }

  function runPreset(preset: Preset, sampleSize: number) {
    const request: SimulateRequest = { scenario_override: preset.scenario, sample_size_per_persona: sampleSize };
    const cached = snapshot.results[preset.id];
    if (!cached) return runLive(preset.title, request);
    execute(
      { label: preset.title, source: "cached", request, expectedShoppers: cached.metrics.total_shoppers_simulated },
      async () => cached,
      CACHED_PRESET_DELAY_MS,
    );
  }

  const llmMode = health && health !== "offline" ? health.llm_mode : null;

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand" onClick={() => { setTab("simulate"); setView("input"); }}>
          <span className="logo">P</span>
          <div>
            <strong>ParallelShop</strong>
            <small>AI digital twin for retail decisions</small>
          </div>
        </div>
        <nav className="tabs">
          <button className={tab === "simulate" ? "active" : ""} onClick={() => setTab("simulate")}>Simulator</button>
          <button className={tab === "credibility" ? "active" : ""} onClick={() => setTab("credibility")}>Back-test proof</button>
        </nav>
        <div className={`status ${health === "offline" ? "off" : health ? "on" : ""}`} title={API_BASE}>
          <span className="dot" />
          {health === null ? "Connecting…" : health === "offline" ? "API offline" : llmMode === "gemini" ? "Live · Gemini agents" : "Live · heuristic agents"}
        </div>
      </header>

      <main className="content">
        {tab === "credibility" ? (
          <BacktestPanel cached={snapshot.backtest} />
        ) : view === "loading" && run ? (
          <LoadingView label={run.label} expectedShoppers={run.expectedShoppers} done={loadingDone} />
        ) : view === "results" && result && run ? (
          <Dashboard
            result={result}
            run={run}
            onBack={() => setView("input")}
            onRerunLive={() => runLive(run.label, run.request)}
          />
        ) : (
          <ScenarioInput
            presets={presets}
            cachedIds={new Set(Object.keys(snapshot.results))}
            apiOffline={health === "offline"}
            error={error}
            onRunPrompt={(prompt, quickMode, sampleSize) =>
              runLive(prompt, { prompt, quick_mode: quickMode, sample_size_per_persona: sampleSize })
            }
            onRunPreset={runPreset}
          />
        )}
      </main>

      <footer className="footer">
        Gemini on Vertex AI (persona agents) · Cloud Run (simulation API) · BigQuery (segmentation) · Firebase Hosting
      </footer>
    </div>
  );
}
