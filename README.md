# ParallelShop — AI Digital Twin for Retail Simulation

ParallelShop is an AI-powered simulation engine for retail and quick-commerce. It simulates customer populations using persona-conditioned Gemini agents to test "what-if" store decisions (price hikes, product stockouts/delistings, promotions) before rolling them out in the real world.

---

## Architecture

- **Persona Agents**: Gemini Flash / Vertex AI with memory (top 20 historical items) and behavioral traits (`bargain_hunter`, `brand_loyal`, `bulk_shopper`, `convenience_shopper`).
- **Data & Analytics**: BigQuery (`parallelshop` dataset) for customer purchase histories and segmentation.
- **Simulation Engine**: FastAPI with parallel asynchronous agent orchestration (`asyncio.gather` with concurrency limits).
- **Deployment**: Docker container ready for Google Cloud Run (`asia-south1`).

---

## Directory Structure

```text
├── backend/
│   ├── agent.py          # Gemini persona shopper agent + heuristic simulation fallback
│   ├── backtest.py       # Credibility back-test engine (predicted vs actual)
│   ├── bigquery.py       # BigQuery data store & local cache loader
│   ├── Dockerfile        # Cloud Run production deployment
│   ├── main.py           # FastAPI application endpoints
│   ├── presets.py        # Cached preset demo scenarios
│   ├── requirements.txt  # Python dependencies
│   ├── scenario.py       # Natural language what-if scenario parser
│   └── simulate.py       # Parallel async simulation runner
├── data/
│   ├── sample_dataset.json   # 200 customer personas & catalog
│   ├── schema.sql            # BigQuery DDL schemas
│   ├── segmentation.sql      # BigQuery persona segmentation SQL
│   └── seed_sample_data.py   # Dataset generator / BigQuery seeder
├── frontend/                 # React + Vite dashboard (Firebase Hosting)
│   ├── src/App.tsx           # Screen flow: scenario input → loading → results / back-test
│   ├── src/components/       # Dashboard widgets (revenue chart, churn gauge, substitutions, voices, segments)
│   ├── src/data/snapshot.json # Pre-simulated preset + back-test results (instant demo)
│   ├── scripts/snapshot.mjs  # Regenerates snapshot.json from a live API
│   └── firebase.json         # Firebase Hosting config (SPA rewrite)
├── run_backtest.py       # CLI runner for Step 4 Credibility Back-Test
├── test_backend.py       # End-to-end API test suite
├── .env.example          # Environment variables template
└── .gitignore            # Git ignore rules for keys & temp files
```

---

## Persona Segmentation Rules (BigQuery)

- **`bargain_hunter`**: `price_sensitivity > 60%` (items bought at lowest category price).
- **`brand_loyal`**: `brand_loyalty > 60%` (reorder rate of the same brand).
- **`bulk_shopper`**: `avg_basket_size > 15 items` (family / bulk buyers).
- **`convenience_shopper`**: balanced shopper baseline.

---

## Credibility Back-Test (Day 5–7 Milestone)

To validate system accuracy, we test against historical hold-out stockout events:

```bash
python3 run_backtest.py
```

**Key Credibility Metric**:
> *"Predicted substitution to Standard Bananas: 38.1%, Actual historical: 31.2% (MAE: 4.4%)"*

---

## Quickstart

### 1. Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
```

### 2. Generate / Seed Data
```bash
python3 data/seed_sample_data.py
```

### 3. Run FastAPI Backend
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
```

Interactive Swagger API docs available at: `http://localhost:8080/docs`

### 4. Deploy to Cloud Run
```bash
gcloud run deploy parallelshop-api \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated
```

---

## Frontend (Step 5)

Three screens: **Scenario input** (free text + preset buttons from `/presets`), **Loading view** (staged progress while agents run), and **Results dashboard** (revenue before/after by persona, churn gauge, substitution flows, customer voices, segment comparison). A **Back-test proof** tab renders `/backtest`.

### Run locally
```bash
cd frontend
npm install
cp .env.example .env.local      # API_PROXY_TARGET = your local FastAPI (default http://localhost:8080)
npm run dev                     # http://localhost:5173
```

### Make preset buttons instant (do this before the demo)
Preset buttons render from `src/data/snapshot.json` when a result is present, otherwise they fall back to a live `/simulate` call. Bake real engine output into the snapshot:
```bash
npm run snapshot -- https://<your-cloud-run-url>   # also captures /backtest
```

### Deploy to Firebase Hosting
```bash
npm install -g firebase-tools
firebase login
echo VITE_API_BASE_URL=https://<your-cloud-run-url> > .env.production
npm run deploy                  # tsc + vite build + firebase deploy --only hosting
```
The project id is set in `frontend/.firebaserc` (`parallelshop-hack`). CORS is already open on the FastAPI app (`allow_origins=["*"]`).
