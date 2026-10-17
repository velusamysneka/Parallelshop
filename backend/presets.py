PRESET_SCENARIOS = [
    {
        "id": "raise_milk_2",
        "title": "Raise Fresh Milk by ₹2",
        "prompt": "Raise Fresh Milk (1L) price by ₹2 across all stores",
        "scenario": {
            "price_changes": [{"product_id": 101, "product_name": "Fresh Milk (1L)", "price_delta": 2.0}],
            "removed_products": [],
            "discount_promotions": [],
            "summary": "Milk price +₹2"
        },
        "cached_metrics": {
            "total_shoppers_simulated": 60,
            "baseline_revenue": 28450.0,
            "simulated_revenue": 29320.0,
            "revenue_delta": 870.0,
            "revenue_delta_pct": 3.1,
            "churn_rate_pct": 2.5,
            "top_substitution": "Fresh Milk (1L) -> Almond Milk (12%)"
        }
    },
    {
        "id": "remove_top_brand",
        "title": "Remove Premium Brand (FarmFresh)",
        "prompt": "Remove FarmFresh brand products due to supplier supply chain disruption",
        "scenario": {
            "price_changes": [],
            "removed_products": [
                {"product_id": 102, "product_name": "Premium Organic Whole Milk (1L)"},
                {"product_id": 201, "product_name": "Organic Bananas (1kg)"},
                {"product_id": 203, "product_name": "Hass Avocados (2 pack)"}
            ],
            "discount_promotions": [],
            "summary": "Remove FarmFresh products"
        },
        "cached_metrics": {
            "total_shoppers_simulated": 60,
            "baseline_revenue": 28450.0,
            "simulated_revenue": 24180.0,
            "revenue_delta": -4270.0,
            "revenue_delta_pct": -15.0,
            "churn_rate_pct": 18.3,
            "top_substitution": "Organic Bananas -> Standard Bananas (34%)"
        }
    },
    {
        "id": "snack_promo_20",
        "title": "20% Off Snacks Weekend Promo",
        "prompt": "20% discount on all snacks aisle items for weekend boost",
        "scenario": {
            "price_changes": [
                {"product_id": 601, "product_name": "Potato Chips Salted (150g)", "price_delta": -6.0},
                {"product_id": 602, "product_name": "Roasted Almonds (250g)", "price_delta": -44.0}
            ],
            "removed_products": [],
            "discount_promotions": [{"target": "Snacks", "discount_pct": 20.0}],
            "summary": "20% off snacks promotion"
        },
        "cached_metrics": {
            "total_shoppers_simulated": 60,
            "baseline_revenue": 28450.0,
            "simulated_revenue": 31200.0,
            "revenue_delta": 2750.0,
            "revenue_delta_pct": 9.7,
            "churn_rate_pct": 0.0,
            "top_substitution": "Increased basket volume on Roasted Almonds"
        }
    }
]
