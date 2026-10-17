export type Persona = "bargain_hunter" | "brand_loyal" | "bulk_shopper" | "convenience_shopper";

export interface Scenario {
  raw_text?: string;
  price_changes?: { product_id?: number; product_name: string; price_delta: number }[];
  removed_products?: { product_id?: number; product_name: string }[];
  discount_promotions?: { target: string; discount_pct: number }[];
  summary?: string;
}

export interface Metrics {
  total_shoppers_simulated: number;
  baseline_revenue: number;
  simulated_revenue: number;
  revenue_delta: number;
  revenue_delta_pct: number;
  baseline_avg_basket: number;
  simulated_avg_basket: number;
  churn_count: number;
  churn_rate_pct: number;
}

export interface SubstitutionFlow {
  source: string;
  target: string;
  count: number;
  percentage: number;
}

export interface PersonaStats {
  shopper_count: number;
  churn_rate: number;
  revenue_before: number;
  revenue_after: number;
  revenue_delta_pct: number;
}

export interface CustomerVoice {
  persona: string;
  action: "buy" | "leave" | string;
  quote: string;
}

export interface SimulationResult {
  status: string;
  scenario: Scenario;
  metrics: Metrics;
  substitution_flows: SubstitutionFlow[];
  persona_breakdown: Partial<Record<Persona, PersonaStats>>;
  customer_voices: CustomerVoice[];
}

export interface Preset {
  id: string;
  title: string;
  prompt: string;
  scenario: Scenario;
}

export interface BacktestRow {
  behavior: string;
  actual_historical_pct: number;
  predicted_agent_pct: number;
  absolute_error_pct: number;
}

export interface BacktestResult {
  status: string;
  event_name: string;
  removed_product: string;
  shoppers_evaluated: number;
  killer_slide_stat: string;
  mean_absolute_error_pct: number;
  comparison: BacktestRow[];
  methodology: string;
}

export interface Health {
  status: string;
  service: string;
  llm_mode: string;
}

export interface SimulateRequest {
  prompt?: string;
  scenario_override?: Scenario;
  quick_mode?: boolean;
  sample_size_per_persona?: number;
}

export interface Snapshot {
  generated_at: string | null;
  api: string | null;
  presets: Preset[];
  results: Record<string, SimulationResult>;
  backtest: BacktestResult | null;
}
