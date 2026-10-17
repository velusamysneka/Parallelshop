import os
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_endpoints():
    print("Testing /health...")
    r = client.get("/health")
    assert r.status_code == 200, f"/health failed: {r.text}"
    print("  -> Health OK:", r.json())

    print("\nTesting /catalog...")
    r = client.get("/catalog")
    assert r.status_code == 200
    catalog = r.json()
    assert len(catalog) > 0
    print(f"  -> Catalog OK ({len(catalog)} items)")

    print("\nTesting /personas...")
    r = client.get("/personas?limit_per_persona=2")
    assert r.status_code == 200
    personas_data = r.json()
    assert "distribution" in personas_data
    print(f"  -> Personas OK: {personas_data['distribution']}")

    print("\nTesting /presets...")
    r = client.get("/presets")
    assert r.status_code == 200
    presets = r.json()
    assert len(presets) == 3
    print(f"  -> Presets OK ({len(presets)} presets available)")

    print("\nTesting /scenario/parse...")
    r = client.post("/scenario/parse", json={"prompt": "raise milk price by 2 and remove white bread"})
    assert r.status_code == 200
    parsed = r.json()
    print("  -> Scenario parse OK:", parsed["summary"])

    print("\nTesting /simulate (quick_mode)...")
    r = client.post("/simulate", json={"prompt": "raise milk price by 2", "quick_mode": True})
    assert r.status_code == 200
    sim = r.json()
    assert sim["status"] == "success"
    print(f"  -> Simulation OK: shoppers={sim['metrics']['total_shoppers_simulated']}, rev_delta%={sim['metrics']['revenue_delta_pct']}%")
    print(f"  -> Customer voices sample: {sim['customer_voices'][0]['quote'][:80]}...")

    print("\nTesting /backtest...")
    r = client.post("/backtest?sample_size_per_persona=10")
    assert r.status_code == 200
    bt = r.json()
    assert bt["status"] == "success"
    print(f"  -> Back-test OK: Killer stat = \"{bt['killer_slide_stat']}\"")

    print("\n" + "=" * 50)
    print("ALL API ENDPOINTS TESTED SUCCESSFULLY!")
    print("=" * 50)

if __name__ == "__main__":
    test_endpoints()
