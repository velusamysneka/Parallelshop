// Runs every preset (and the back-test) against a live ParallelShop API and bakes the
// results into src/data/snapshot.json, so preset buttons render instantly in the demo.
// Usage: npm run snapshot -- https://parallelshop-api-xxxx.a.run.app
import { writeFile } from "node:fs/promises";

const api = (process.argv[2] ?? process.env.VITE_API_BASE_URL ?? "http://localhost:8080").replace(/\/$/, "");
const sampleSize = Number(process.env.SAMPLE_SIZE ?? 15);
const outFile = new URL("../src/data/snapshot.json", import.meta.url);

async function call(path, body) {
  const res = await fetch(`${api}${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} -> ${res.status} ${await res.text()}`);
  return res.json();
}

console.log(`Snapshotting presets from ${api} (sample_size_per_persona=${sampleSize})`);
const presets = (await call("/presets")).map(({ id, title, prompt, scenario }) => ({ id, title, prompt, scenario }));

const results = {};
for (const preset of presets) {
  const result = await call("/simulate", { scenario_override: preset.scenario, sample_size_per_persona: sampleSize });
  results[preset.id] = result;
  console.log(`  ${preset.id}: ${result.metrics.total_shoppers_simulated} shoppers, revenue ${result.metrics.revenue_delta_pct}%, churn ${result.metrics.churn_rate_pct}%`);
}

const backtest = await call("/backtest?sample_size_per_persona=25", {});
console.log(`  backtest: ${backtest.killer_slide_stat}`);

await writeFile(
  outFile,
  JSON.stringify({ generated_at: new Date().toISOString(), api, presets, results, backtest }, null, 2) + "\n",
);
console.log(`Wrote ${outFile.pathname}`);
