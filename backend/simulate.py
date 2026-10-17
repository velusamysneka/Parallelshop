import asyncio
from typing import Dict, Any, List
from .agent import simulate_single_shopper
from .bigquery import BigQueryDataStore

async def run_simulation(
    scenario: Dict[str, Any],
    quick_mode: bool = False,
    sample_size_per_persona: int = 15
) -> Dict[str, Any]:
    store = BigQueryDataStore()
    catalog = store.get_catalog()
    
    limit = 5 if quick_mode else sample_size_per_persona
    customers = store.get_customers(limit_per_persona=limit)
    
    # Calculate baseline for these customers
    baseline_revenue = 0.0
    baseline_items_count = 0
    for c in customers:
        c_items = c.get("top_products", [])
        baseline_revenue += sum(item.get("price", 50.0) for item in c_items)
        baseline_items_count += len(c_items)

    avg_baseline_basket = baseline_items_count / max(len(customers), 1)

    # Concurrency limiter
    semaphore = asyncio.Semaphore(15)

    async def _worker(cust: Dict[str, Any]) -> Dict[str, Any]:
        async with semaphore:
            return await simulate_single_shopper(cust, scenario, catalog)

    tasks = [_worker(c) for c in customers]
    shopper_results = await asyncio.gather(*tasks)

    # Aggregations
    simulated_revenue = 0.0
    simulated_items_count = 0
    churn_count = 0
    substitutions_map: Dict[str, Dict[str, int]] = {}
    persona_stats: Dict[str, Dict[str, Any]] = {
        "bargain_hunter": {"count": 0, "churn": 0, "rev_before": 0.0, "rev_after": 0.0},
        "brand_loyal": {"count": 0, "churn": 0, "rev_before": 0.0, "rev_after": 0.0},
        "bulk_shopper": {"count": 0, "churn": 0, "rev_before": 0.0, "rev_after": 0.0},
        "convenience_shopper": {"count": 0, "churn": 0, "rev_before": 0.0, "rev_after": 0.0},
    }
    customer_voices: List[Dict[str, str]] = []
    seen_personas_in_voices = set()

    for idx, res in enumerate(shopper_results):
        p_name = res.get("persona", "convenience_shopper")
        cust_baseline_rev = sum(item.get("price", 50.0) for item in customers[idx].get("top_products", []))
        
        if p_name in persona_stats:
            persona_stats[p_name]["count"] += 1
            persona_stats[p_name]["rev_before"] += cust_baseline_rev

        if res.get("action") == "leave":
            churn_count += 1
            if p_name in persona_stats:
                persona_stats[p_name]["churn"] += 1
        else:
            basket = res.get("basket", [])
            cart_rev = sum(item.get("price", 0.0) * item.get("quantity", 1) for item in basket)
            simulated_revenue += cart_rev
            simulated_items_count += sum(item.get("quantity", 1) for item in basket)
            if p_name in persona_stats:
                persona_stats[p_name]["rev_after"] += cart_rev

        for sub in res.get("substitutions", []):
            src = sub.get("from_product", "Unknown")
            dst = sub.get("to_product", "Unknown")
            substitutions_map.setdefault(src, {})
            substitutions_map[src][dst] = substitutions_map[src].get(dst, 0) + 1

        # Collect diverse quotes
        if p_name not in seen_personas_in_voices and res.get("reasoning"):
            customer_voices.append({
                "persona": p_name,
                "action": res.get("action"),
                "quote": res.get("reasoning")
            })
            seen_personas_in_voices.add(p_name)

    total_shoppers = len(shopper_results)
    churn_rate = round((churn_count / max(total_shoppers, 1)) * 100, 1)
    rev_delta = simulated_revenue - baseline_revenue
    rev_delta_pct = round((rev_delta / max(baseline_revenue, 1.0)) * 100, 1)
    avg_sim_basket = round(simulated_items_count / max(total_shoppers - churn_count, 1), 1)

    # Format substitutions for Sankey or flow table
    substitution_flows = []
    for src, targets in substitutions_map.items():
        total_subs = sum(targets.values())
        for dst, count in targets.items():
            pct = round((count / total_subs) * 100, 1)
            substitution_flows.append({
                "source": src,
                "target": dst,
                "count": count,
                "percentage": pct
            })
    substitution_flows.sort(key=lambda x: x["count"], reverse=True)

    # Format persona metrics
    persona_breakdown = {}
    for p_name, stats in persona_stats.items():
        c_count = stats["count"]
        if c_count > 0:
            persona_breakdown[p_name] = {
                "shopper_count": c_count,
                "churn_rate": round((stats["churn"] / c_count) * 100, 1),
                "revenue_before": round(stats["rev_before"], 2),
                "revenue_after": round(stats["rev_after"], 2),
                "revenue_delta_pct": round(((stats["rev_after"] - stats["rev_before"]) / max(stats["rev_before"], 1.0)) * 100, 1)
            }

    return {
        "status": "success",
        "scenario": scenario,
        "metrics": {
            "total_shoppers_simulated": total_shoppers,
            "baseline_revenue": round(baseline_revenue, 2),
            "simulated_revenue": round(simulated_revenue, 2),
            "revenue_delta": round(rev_delta, 2),
            "revenue_delta_pct": rev_delta_pct,
            "baseline_avg_basket": round(avg_baseline_basket, 1),
            "simulated_avg_basket": avg_sim_basket,
            "churn_count": churn_count,
            "churn_rate_pct": churn_rate
        },
        "substitution_flows": substitution_flows,
        "persona_breakdown": persona_breakdown,
        "customer_voices": customer_voices
    }
