import type { BacktestResult, Health, Preset, SimulateRequest, SimulationResult } from "./types";

// In dev, default to the Vite proxy (/api -> API_PROXY_TARGET); in production builds set VITE_API_BASE_URL.
export const API_BASE = (import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? "/api" : "http://localhost:8080")).replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<Health>("/health"),
  presets: () => request<Preset[]>("/presets"),
  simulate: (body: SimulateRequest) =>
    request<SimulationResult>("/simulate", { method: "POST", body: JSON.stringify(body) }),
  backtest: (sampleSizePerPersona = 25) =>
    request<BacktestResult>(`/backtest?sample_size_per_persona=${sampleSizePerPersona}`, { method: "POST" }),
};
