import type { Persona } from "./types";

export const PERSONAS: Persona[] = ["bargain_hunter", "brand_loyal", "bulk_shopper", "convenience_shopper"];

export const PERSONA_META: Record<Persona, { label: string; color: string; blurb: string }> = {
  bargain_hunter: { label: "Bargain Hunters", color: "#f59e0b", blurb: "Switch to the cheapest option at the first price hike" },
  brand_loyal: { label: "Brand Loyalists", color: "#8b5cf6", blurb: "Stick with favourite brands, tolerate up to ~20% hikes" },
  bulk_shopper: { label: "Bulk Shoppers", color: "#10b981", blurb: "Large family baskets, prioritise staples and volume" },
  convenience_shopper: { label: "Convenience Shoppers", color: "#3b82f6", blurb: "Balanced, substitute common items easily" },
};

export const personaMeta = (p: string) =>
  PERSONA_META[p as Persona] ?? { label: p, color: "#94a3b8", blurb: "" };

const inr = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });
export const formatINR = (n: number) => inr.format(n);

export const formatPct = (n: number, signed = false) => `${signed && n > 0 ? "+" : ""}${n.toFixed(1)}%`;

export const deltaClass = (n: number) => (n > 0 ? "pos" : n < 0 ? "neg" : "neutral");
