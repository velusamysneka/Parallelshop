#!/usr/bin/env python3
import json
import random
import os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = DATA_DIR / "sample_dataset.json"

CATALOG = [
    {"product_id": 101, "product_name": "Fresh Milk (1L)", "aisle": "Dairy", "price": 45.0, "brand": "Everyday"},
    {"product_id": 102, "product_name": "Premium Organic Whole Milk (1L)", "aisle": "Dairy", "price": 68.0, "brand": "FarmFresh"},
    {"product_id": 103, "product_name": "Almond Milk Unsweetened (1L)", "aisle": "Dairy", "price": 85.0, "brand": "Nutty"},
    {"product_id": 201, "product_name": "Organic Bananas (1kg)", "aisle": "Produce", "price": 40.0, "brand": "FarmFresh"},
    {"product_id": 202, "product_name": "Standard Bananas (1kg)", "aisle": "Produce", "price": 28.0, "brand": "Everyday"},
    {"product_id": 203, "product_name": "Hass Avocados (2 pack)", "aisle": "Produce", "price": 120.0, "brand": "FarmFresh"},
    {"product_id": 204, "product_name": "Tomatoes (1kg)", "aisle": "Produce", "price": 30.0, "brand": "Everyday"},
    {"product_id": 301, "product_name": "White Bread Loaf", "aisle": "Bakery", "price": 25.0, "brand": "Everyday"},
    {"product_id": 302, "product_name": "100% Whole Wheat Artisan Bread", "aisle": "Bakery", "price": 55.0, "brand": "BakeHouse"},
    {"product_id": 401, "product_name": "Greek Plain Yogurt (500g)", "aisle": "Dairy", "price": 90.0, "brand": "GreekGold"},
    {"product_id": 402, "product_name": "Classic Curd (500g)", "aisle": "Dairy", "price": 35.0, "brand": "Everyday"},
    {"product_id": 501, "product_name": "Bulk Basmati Rice (5kg)", "aisle": "Grains", "price": 350.0, "brand": "RoyalHarvest"},
    {"product_id": 502, "product_name": "Economy White Rice (5kg)", "aisle": "Grains", "price": 210.0, "brand": "Everyday"},
    {"product_id": 503, "product_name": "Rolled Oats (1kg)", "aisle": "Grains", "price": 140.0, "brand": "OatyBest"},
    {"product_id": 601, "product_name": "Potato Chips Salted (150g)", "aisle": "Snacks", "price": 30.0, "brand": "Crispy"},
    {"product_id": 602, "product_name": "Roasted Almonds (250g)", "aisle": "Snacks", "price": 220.0, "brand": "Nutty"},
    {"product_id": 603, "product_name": "Sparkling Cola (2L)", "aisle": "Beverages", "price": 40.0, "brand": "PopCo"},
    {"product_id": 604, "product_name": "Cold Brew Coffee (500ml)", "aisle": "Beverages", "price": 110.0, "brand": "BakeHouse"},
]

def generate_personas(num_users=200):
    random.seed(42)
    users = []
    persona_types = ["bargain_hunter", "brand_loyal", "bulk_shopper", "convenience_shopper"]
    
    for user_id in range(1, num_users + 1):
        assigned_persona = persona_types[(user_id - 1) % len(persona_types)]
        
        if assigned_persona == "bargain_hunter":
            price_sens = round(random.uniform(0.65, 0.95), 2)
            brand_loyalty = round(random.uniform(0.15, 0.45), 2)
            basket_size = round(random.uniform(4.0, 9.0), 1)
            # prefers cheapest items (Everyday brand)
            pool = [p for p in CATALOG if p["brand"] == "Everyday" or p["price"] < 45.0]
        elif assigned_persona == "brand_loyal":
            price_sens = round(random.uniform(0.10, 0.35), 2)
            brand_loyalty = round(random.uniform(0.65, 0.95), 2)
            basket_size = round(random.uniform(5.0, 11.0), 1)
            # sticks to premium brands (FarmFresh, BakeHouse, GreekGold)
            pool = [p for p in CATALOG if p["brand"] in ["FarmFresh", "BakeHouse", "GreekGold"]]
        elif assigned_persona == "bulk_shopper":
            price_sens = round(random.uniform(0.35, 0.60), 2)
            brand_loyalty = round(random.uniform(0.30, 0.60), 2)
            basket_size = round(random.uniform(15.5, 24.0), 1)
            # buys grains, staples, multi-packs
            pool = CATALOG
        else: # convenience_shopper
            price_sens = round(random.uniform(0.25, 0.55), 2)
            brand_loyalty = round(random.uniform(0.25, 0.55), 2)
            basket_size = round(random.uniform(6.0, 12.0), 1)
            pool = CATALOG

        # Pick top 6-10 recurring products
        top_k = random.sample(pool, min(len(pool), random.randint(6, 10)))
        top_products = [
            {
                "product_id": p["product_id"],
                "product_name": p["product_name"],
                "price": p["price"],
                "brand": p["brand"],
                "purchase_count": random.randint(8, 25)
            }
            for p in top_k
        ]
        top_products.sort(key=lambda x: x["purchase_count"], reverse=True)

        users.append({
            "user_id": user_id,
            "persona": assigned_persona,
            "price_sensitivity": price_sens,
            "brand_loyalty": brand_loyalty,
            "avg_basket_size": basket_size,
            "top_products": top_products
        })
    
    return users

def main():
    users = generate_personas(200)
    dataset = {
        "catalog": CATALOG,
        "users": users,
        "summary": {
            "total_users": len(users),
            "catalog_size": len(CATALOG),
            "personas_count": {
                "bargain_hunter": len([u for u in users if u["persona"] == "bargain_hunter"]),
                "brand_loyal": len([u for u in users if u["persona"] == "brand_loyal"]),
                "bulk_shopper": len([u for u in users if u["persona"] == "bulk_shopper"]),
                "convenience_shopper": len([u for u in users if u["persona"] == "convenience_shopper"]),
            }
        }
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Sample data generated: {OUTPUT_FILE} with {len(users)} users.")

if __name__ == "__main__":
    main()
