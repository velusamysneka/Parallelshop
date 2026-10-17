import os
import json
import random
from typing import Dict, Any, List

SYSTEM_PROMPT = """You are simulating an individual grocery shopper in a supermarket.
Your decisions must reflect your assigned shopper persona:
- bargain_hunter: Ultra price-sensitive. If an item becomes expensive, switch to the cheapest alternative in that category, or drop it.
- brand_loyal: Highly loyal to favorite brands. Tolerates price increases up to 20%. If your favorite product is completely removed, try the closest high-end brand or abandon shopping in frustration.
- bulk_shopper: Prioritizes basket volume and staples. Replaces removed items with bulk/economy packs.
- convenience_shopper: Balanced shopper. Accepts moderate price changes, substitutes common items easily.

Output STRICT JSON ONLY matching:
{
  "action": "buy" | "leave",
  "basket": [
    {"product_id": int, "product_name": str, "price": float, "quantity": int}
  ],
  "substitutions": [
    {"from_product": str, "to_product": str, "reason": str}
  ],
  "reasoning": "A 1-2 sentence first-person explanation of what you decided and why."
}
"""

def heuristic_simulate_customer(customer: Dict[str, Any], scenario: Dict[str, Any], catalog: List[Dict[str, Any]]) -> Dict[str, Any]:
    persona = customer.get("persona", "convenience_shopper")
    top_products = customer.get("top_products", [])
    price_sensitivity = customer.get("price_sensitivity", 0.5)
    
    removed_ids = {r["product_id"] for r in scenario.get("removed_products", []) if "product_id" in r}
    removed_names = {r["product_name"].lower() for r in scenario.get("removed_products", []) if "product_name" in r}
    
    price_map = {p["product_id"]: p["price"] for p in catalog}
    for pc in scenario.get("price_changes", []):
        if "product_id" in pc and pc["product_id"] in price_map:
            price_map[pc["product_id"]] += pc.get("price_delta", 0.0)

    basket = []
    substitutions = []
    dropped_count = 0

    catalog_by_aisle: Dict[str, List[Dict[str, Any]]] = {}
    catalog_by_id: Dict[int, Dict[str, Any]] = {}
    for p in catalog:
        catalog_by_aisle.setdefault(p.get("aisle", "General"), []).append(p)
        catalog_by_id[p["product_id"]] = p

    for item in top_products:
        pid = item["product_id"]
        pname = item["product_name"]
        cat_info = catalog_by_id.get(pid, {})
        aisle = cat_info.get("aisle", item.get("aisle", "General"))
        current_price = price_map.get(pid, item.get("price", 50.0))
        base_price = item.get("price", current_price)

        is_removed = (pid in removed_ids) or any(rn in pname.lower() for rn in removed_names)

        if is_removed:
            # Handle removal based on persona
            # Candidate substitutes in the same aisle/category
            aisle_items = [p for p in catalog_by_aisle.get(aisle, []) if p["product_id"] != pid and p["product_id"] not in removed_ids]
            
            # Find same-category items (e.g. bananas -> other bananas)
            same_category_items = [p for p in aisle_items if any(word in p["product_name"].lower() for word in pname.lower().split() if len(word) > 4)]
            
            if persona == "brand_loyal":
                # Brand loyals drop when favorite brand is gone 55% of the time
                if random.random() < 0.55:
                    dropped_count += 1
                    continue
                same_brand = [p for p in aisle_items if p.get("brand") == item.get("brand")]
                if same_brand:
                    sub = same_brand[0]
                elif same_category_items:
                    sub = same_category_items[0]
                elif aisle_items:
                    sub = max(aisle_items, key=lambda x: x["price"])
                else:
                    dropped_count += 1
                    continue

                basket.append({"product_id": sub["product_id"], "product_name": sub["product_name"], "price": price_map.get(sub["product_id"], sub["price"]), "quantity": 1})
                substitutions.append({"from_product": pname, "to_product": sub["product_name"], "reason": "Favorite removed; switched to closest brand/category alternative"})

            elif persona == "bargain_hunter":
                # Bargain hunters substitute to cheapest option
                if random.random() < 0.35:
                    dropped_count += 1
                    continue
                candidates = same_category_items if same_category_items else aisle_items
                if candidates:
                    sub = min(candidates, key=lambda x: price_map.get(x["product_id"], x["price"]))
                    basket.append({"product_id": sub["product_id"], "product_name": sub["product_name"], "price": price_map.get(sub["product_id"], sub["price"]), "quantity": 1})
                    substitutions.append({"from_product": pname, "to_product": sub["product_name"], "reason": "Original gone; grabbed lowest priced option"})
                else:
                    dropped_count += 1

            elif persona == "bulk_shopper":
                if random.random() < 0.40:
                    dropped_count += 1
                    continue
                candidates = same_category_items if same_category_items else aisle_items
                if candidates:
                    sub = candidates[0]
                    basket.append({"product_id": sub["product_id"], "product_name": sub["product_name"], "price": price_map.get(sub["product_id"], sub["price"]), "quantity": 1})
                    substitutions.append({"from_product": pname, "to_product": sub["product_name"], "reason": "Needed substitute for regular bulk staple"})
                else:
                    dropped_count += 1

            else:  # convenience_shopper
                if random.random() < 0.42:
                    dropped_count += 1
                    continue
                candidates = same_category_items if same_category_items else aisle_items
                if candidates:
                    sub = candidates[0]
                    basket.append({"product_id": sub["product_id"], "product_name": sub["product_name"], "price": price_map.get(sub["product_id"], sub["price"]), "quantity": 1})
                    substitutions.append({"from_product": pname, "to_product": sub["product_name"], "reason": "Convenient substitute chosen"})
                else:
                    dropped_count += 1

        else:
            # Item is present. Check price increase reaction
            price_hike_ratio = (current_price - base_price) / max(base_price, 1.0)
            if price_hike_ratio > 0.03:
                if persona == "bargain_hunter" and price_hike_ratio >= 0.05:
                    # Switch to cheaper option or drop
                    aisle_items = [p for p in catalog_by_aisle.get(aisle, catalog) if price_map.get(p["product_id"], p["price"]) < current_price]
                    if aisle_items:
                        sub = min(aisle_items, key=lambda x: price_map.get(x["product_id"], x["price"]))
                        basket.append({"product_id": sub["product_id"], "product_name": sub["product_name"], "price": price_map.get(sub["product_id"], sub["price"]), "quantity": 1})
                        substitutions.append({"from_product": pname, "to_product": sub["product_name"], "reason": f"Price rose to ₹{current_price}; downgraded to save cash"})
                    else:
                        dropped_count += 1
                elif persona == "brand_loyal":
                    # Keep buying even with price hike
                    basket.append({"product_id": pid, "product_name": pname, "price": current_price, "quantity": 1})
                else:
                    basket.append({"product_id": pid, "product_name": pname, "price": current_price, "quantity": 1})
            else:
                basket.append({"product_id": pid, "product_name": pname, "price": current_price, "quantity": 1})

    # Churn threshold: if more than 40% of basket dropped
    if len(basket) == 0 or (len(top_products) > 0 and dropped_count / len(top_products) >= 0.45):
        action = "leave"
        reasoning = f"As a {persona}, the store was missing key items or prices surged beyond acceptable bounds. Left without purchasing."
        basket = []
    else:
        action = "buy"
        if substitutions:
            reasoning = f"As a {persona}, adapted my cart: substituted {substitutions[0]['from_product']} for {substitutions[0]['to_product']}."
        else:
            reasoning = f"As a {persona}, prices and stock were acceptable, completed regular basket."

    return {
        "user_id": customer.get("user_id"),
        "persona": persona,
        "action": action,
        "basket": basket,
        "substitutions": substitutions,
        "reasoning": reasoning
    }

async def simulate_single_shopper(customer: Dict[str, Any], scenario: Dict[str, Any], catalog: List[Dict[str, Any]]) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    use_mock = os.getenv("USE_MOCK_GEMINI", "false").lower() == "true"

    if not api_key or use_mock:
        return heuristic_simulate_customer(customer, scenario, catalog)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        user_prompt = f"""
        Customer Profile:
        - Persona: {customer['persona']} (price_sensitivity: {customer.get('price_sensitivity', 0.5)}, brand_loyalty: {customer.get('brand_loyalty', 0.5)})
        - Top regular purchases: {[p['product_name'] for p in customer.get('top_products', [])]}

        Store Changes (Scenario):
        {json.dumps(scenario)}

        Available Store Catalog:
        {json.dumps([{'id': c['product_id'], 'name': c['product_name'], 'price': c['price'], 'brand': c.get('brand', '')} for c in catalog])}

        Decide whether to buy or leave, which items to purchase, substitutions made, and first-person reasoning.
        """

        response = await model.generate_content_async([SYSTEM_PROMPT, user_prompt])
        cleaned = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        data["user_id"] = customer.get("user_id")
        data["persona"] = customer.get("persona")
        return data
    except Exception:
        return heuristic_simulate_customer(customer, scenario, catalog)
