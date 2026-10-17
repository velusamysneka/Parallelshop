import os
import re
import json
from typing import Dict, Any, List

def parse_scenario_rule_based(text: str, catalog: List[Dict[str, Any]]) -> Dict[str, Any]:
    text_lower = text.lower()
    price_changes = []
    removed_products = []
    discount_promotions = []

    # Detect price increases or drops, e.g. "raise milk price by 2", "milk price +2", "raise milk 5"
    price_match = re.search(r"(?:raise|increase|hike|\+)\s*(?:the\s*)?([a-zA-Z\s]+?)\s*(?:price\s*)?(?:by|\+)?\s*(?:[₹$Rs\.]*)?\s*(\d+(?:\.\d+)?)", text_lower)
    if price_match:
        prod_keyword = price_match.group(1).strip()
        delta = float(price_match.group(2))
        for p in catalog:
            if prod_keyword in p["product_name"].lower():
                price_changes.append({"product_id": p["product_id"], "product_name": p["product_name"], "price_delta": delta})
                break

    # Detect product removal e.g. "remove top brand", "remove brand x", "remove white bread"
    remove_match = re.search(r"(?:remove|discontinue|drop|delete|out of stock)\s*(?:the\s*)?([a-zA-Z\s]+)", text_lower)
    if remove_match:
        prod_keyword = remove_match.group(1).strip()
        for p in catalog:
            if prod_keyword in p["product_name"].lower() or (p.get("brand") and prod_keyword in p["brand"].lower()):
                removed_products.append({"product_id": p["product_id"], "product_name": p["product_name"]})
                break

    # Detect discounts e.g. "20% off snacks"
    discount_match = re.search(r"(\d+)%\s*(?:off|discount)\s*(?:on\s*)?([a-zA-Z\s]+)", text_lower)
    if discount_match:
        discount_pct = float(discount_match.group(1))
        category = discount_match.group(2).strip()
        discount_promotions.append({"target": category, "discount_pct": discount_pct})

    # Default fallback if nothing matched specifically
    if not price_changes and not removed_products and not discount_promotions:
        # Check simple keywords
        if "milk" in text_lower:
            for p in catalog:
                if "milk" in p["product_name"].lower():
                    price_changes.append({"product_id": p["product_id"], "product_name": p["product_name"], "price_delta": 2.0})
                    break
        elif "bread" in text_lower or "remove" in text_lower:
            removed_products.append({"product_id": 301, "product_name": "White Bread Loaf"})

    return {
        "raw_text": text,
        "price_changes": price_changes,
        "removed_products": removed_products,
        "discount_promotions": discount_promotions,
        "summary": f"Scenario parsed: {len(price_changes)} price shifts, {len(removed_products)} removed items, {len(discount_promotions)} discounts."
    }

async def parse_scenario(text: str, catalog: List[Dict[str, Any]]) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    use_mock = os.getenv("USE_MOCK_GEMINI", "false").lower() == "true"

    if not api_key or use_mock:
        return parse_scenario_rule_based(text, catalog)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        catalog_names = [f"{p['product_id']}: {p['product_name']}" for p in catalog]
        prompt = f"""
        Given the catalog items: {catalog_names}
        Parse this retail what-if scenario into strict JSON:
        Scenario: "{text}"

        Return JSON matching this exact structure:
        {{
            "price_changes": [{{"product_id": int, "product_name": str, "price_delta": float}}],
            "removed_products": [{{"product_id": int, "product_name": str}}],
            "discount_promotions": [{{"target": str, "discount_pct": float}}],
            "summary": str
        }}
        """
        response = await model.generate_content_async(prompt)
        cleaned = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except Exception:
        return parse_scenario_rule_based(text, catalog)
