import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_dataset.json"

class BigQueryDataStore:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = os.getenv("BIGQUERY_DATASET", "parallelshop")
        self.client = None
        
        # Try initializing BigQuery if credentials exist
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and self.project_id:
            try:
                from google.cloud import bigquery
                self.client = bigquery.Client(project=self.project_id)
            except Exception:
                self.client = None

        self._local_cache: Optional[Dict[str, Any]] = None

    def _load_local_data(self) -> Dict[str, Any]:
        if self._local_cache is None:
            if not DATA_FILE.exists():
                raise FileNotFoundError(f"Local sample data missing at {DATA_FILE}. Run data/seed_sample_data.py first.")
            with open(DATA_FILE, "r") as f:
                self._local_cache = json.load(f)
        return self._local_cache

    def get_catalog(self) -> List[Dict[str, Any]]:
        if self.client:
            try:
                query = f"SELECT product_id, product_name, aisle_id, department_id, price FROM `{self.project_id}.{self.dataset_id}.products`"
                rows = self.client.query(query).result()
                return [dict(row) for row in rows]
            except Exception:
                pass
        return self._load_local_data().get("catalog", [])

    def get_customers(self, persona: Optional[str] = None, limit_per_persona: int = 15) -> List[Dict[str, Any]]:
        if self.client:
            try:
                condition = f"WHERE persona = '{persona}'" if persona else ""
                query = f"""
                    SELECT user_id, price_sensitivity, brand_loyalty, avg_basket_size, persona, top_products
                    FROM `{self.project_id}.{self.dataset_id}.customer_personas`
                    {condition}
                    LIMIT 200
                """
                rows = self.client.query(query).result()
                result = []
                for row in rows:
                    item = dict(row)
                    if isinstance(item.get("top_products"), str):
                        item["top_products"] = json.loads(item["top_products"])
                    result.append(item)
                return result
            except Exception:
                pass

        data = self._load_local_data()
        users = data.get("users", [])
        if persona:
            filtered = [u for u in users if u["persona"] == persona]
            return filtered[:limit_per_persona]

        # Return balanced sample across personas
        selected = []
        for p_type in ["bargain_hunter", "brand_loyal", "bulk_shopper", "convenience_shopper"]:
            cohort = [u for u in users if u["persona"] == p_type][:limit_per_persona]
            selected.extend(cohort)
        return selected

    def get_persona_distribution(self) -> Dict[str, int]:
        data = self._load_local_data()
        return data.get("summary", {}).get("personas_count", {})
