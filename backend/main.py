import os
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from .scenario import parse_scenario
from .simulate import run_simulation
from .bigquery import BigQueryDataStore
from .presets import PRESET_SCENARIOS
from .backtest import run_backtest

app = FastAPI(
    title="ParallelShop Simulation Engine",
    description="Multi-agent grocery twin powered by Gemini, BigQuery, and Cloud Run",
    version="1.0.0"
)

# CORS setup for Firebase Hosting and local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScenarioRequest(BaseModel):
    prompt: Optional[str] = None
    scenario_override: Optional[Dict[str, Any]] = None
    quick_mode: bool = False
    sample_size_per_persona: int = 15

class ParseRequest(BaseModel):
    prompt: str

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ParallelShop API",
        "llm_mode": "mock_or_heuristic" if os.getenv("USE_MOCK_GEMINI") == "true" or not os.getenv("GEMINI_API_KEY") else "gemini"
    }

@app.get("/catalog")
def get_catalog():
    store = BigQueryDataStore()
    return store.get_catalog()

@app.get("/personas")
def get_personas(limit_per_persona: int = Query(5, ge=1, le=50)):
    store = BigQueryDataStore()
    return {
        "distribution": store.get_persona_distribution(),
        "sample_customers": store.get_customers(limit_per_persona=limit_per_persona)
    }

@app.get("/presets")
def get_preset_scenarios():
    return PRESET_SCENARIOS

@app.post("/scenario/parse")
async def parse_scenario_endpoint(req: ParseRequest):
    store = BigQueryDataStore()
    catalog = store.get_catalog()
    parsed = await parse_scenario(req.prompt, catalog)
    return parsed

@app.post("/simulate")
async def simulate_endpoint(req: ScenarioRequest):
    store = BigQueryDataStore()
    catalog = store.get_catalog()

    if req.scenario_override:
        scenario = req.scenario_override
    elif req.prompt:
        scenario = await parse_scenario(req.prompt, catalog)
    else:
        raise HTTPException(status_code=400, detail="Either 'prompt' or 'scenario_override' must be provided.")

    results = await run_simulation(
        scenario=scenario,
        quick_mode=req.quick_mode,
        sample_size_per_persona=req.sample_size_per_persona
    )
    return results

@app.post("/backtest")
async def backtest_endpoint(sample_size_per_persona: int = Query(25, ge=5, le=50)):
    results = await run_backtest(sample_size_per_persona=sample_size_per_persona)
    return results

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
