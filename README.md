# SwasthyaSetu

**Track: Smart Health** — AI-driven health centre & supply chain management for a district's PHCs/CHCs.

## Problem statement

District health officers overseeing a network of Primary Health Centres (PHCs) and Community Health Centres (CHCs) have no real-time visibility into three recurring failure modes:

- **Medicine stock-outs** that go unnoticed until a patient is turned away, because nobody is forecasting consumption against remaining stock.
- **Unmanaged footfall and bed pressure** — some centres are quietly overcrowded while nearby centres have spare capacity, with no district-level view to rebalance.
- **Unpredictable doctor attendance and stock imbalance across centres**, with no automatic way to flag an underperforming centre before it becomes a crisis, or to suggest which nearby centre could redistribute surplus medicine to cover a shortfall.

Meanwhile, the frontline staff who hold the data staff intake happens on paper or ad-hoc phone calls, in a country where the reporting staff's working language is regional, not English, and typing on a phone is often slower than speaking.

**SwasthyaSetu** closes both gaps: a mobile-first staff app for daily intake (voice or text, regional-language-first) feeding a statistical ML pipeline that gives district officers early stock-out warnings, demand forecasts, redistribution recommendations, and automatic flagging of underperforming centres.

## Who it serves

```
PHC/CHC staff  --daily intake (voice/text)-->  District health officers  --redistribution & policy decisions-->  Patients
                                                       |
                                                       v
                                          MPs / district administration
                                          (oversight, budget, scale-up decisions)
```

- **PHC/CHC staff**: log daily stock/footfall/attendance in under a minute, report incidents by voice in their own language.
- **District health officers**: one dashboard showing every centre's health score, active alerts, and where to redistribute surplus medicine.
- **Patients**: the actual beneficiaries — fewer stock-outs, less overcrowding, more predictable care.
- **District/state administration (MPs' offices)**: a scalable, low-cost model for oversight across many districts.

## Architecture

```mermaid
flowchart TB
    subgraph L1["Layer 1 — Data ingestion"]
        Staff["Staff PWA\n(frontend/staff)"] -->|REST| API["FastAPI\n(api/)"]
        Voice["Voice note"] --> STT["Speech-to-Text"] --> Translate["Translation -> English"] --> API
    end

    subgraph L2["Layer 2 — Storage"]
        DB[("Firestore / local JSON\n5 collections:\ncentres, daily_logs, stock_items,\nalerts, redistribution_recommendations")]
    end

    subgraph L3["Layer 3 — ML pipeline"]
        Forecaster["ml/forecaster.py\nexponential smoothing (statsmodels)\ndays-to-stockout, 7-day footfall"]
        Scorer["ml/scorer.py\ncomposite z-score -> 0-100 health score"]
        Recommender["ml/recommender.py\ngreedy surplus<->deficit matching"]
        Gemini["gemini/*\nexplains / translates / tags\nthe numbers above only"]
    end

    subgraph L4["Layer 4 — API"]
        Orchestration["Orchestration endpoint\nforecast -> score -> recommend -> summarize"]
    end

    subgraph L5["Layer 5 — Frontend"]
        Admin["frontend/admin\nDistrict dashboard\n(React + Vite + Tailwind)"]
        StaffUI["frontend/staff\nMobile intake PWA"]
    end

    API --> DB
    DB --> Forecaster --> Scorer --> Recommender --> Gemini --> Orchestration
    Orchestration --> Admin
    API --> StaffUI
```

Real statistical ML (exponential smoothing, z-score scoring, greedy matching) does the forecasting, scoring, and redistribution math; Gemini only explains/translates/tags outputs that already exist. Deployable for free on Firebase Hosting (frontends) + Render.com (backend), with Firestore/Cloud Run as the drop-in upgrade path once GCP credits are available.

### Gemini separation (important)

`gemini/` only ever receives numbers already computed by `ml/`: a health score, a list of `days_to_stockout`, a footfall total, an already-decided alert category/severity. It drafts the natural-language summary/alert text around those numbers, or extracts structured tags from a staff incident note (the one place it reads raw text, since there's no statistical model for free text). **It never decides a score or a forecast.** This is enforced by the function signatures in `gemini/summarizer.py`, `gemini/alert_drafter.py`, `gemini/incident_tagger.py` — see `gemini/tests/` for tests that assert on the exact prompt contents.

If `GEMINI_API_KEY` isn't set, every Gemini call falls back to a templated message (orchestration) or an `"other"`/`"medium"` tag (incident intake) — the numeric pipeline and the rest of the app keep working.

## ML pipeline, explained for judges

All three modules in `ml/` are pure functions — no network calls, no Firestore, no Gemini — and are unit tested in `ml/tests/` in isolation from the rest of the stack.

| Module | What it computes | Method |
|---|---|---|
| `forecaster.py` | Per-medicine days-to-stockout, 7-day-ahead footfall | Simple exponential smoothing on the consumption series for stockout; Holt-Winters with weekly seasonality (falls back to simple smoothing under 21 days of history) for footfall |
| `scorer.py` | 0-100 health score per centre | Averages 4 metrics (stock availability, doctor attendance rate, bed availability, test-kit availability) over a 14-day window, computes a z-score for each metric relative to that day's district peer average, then maps the composite z-score through the normal CDF to a 0-100 score |
| `recommender.py` | Which centre should send how much of which medicine, to where | Greedy matching: centres below their reorder threshold are served most-urgent-first, matched to the nearest centre with stock above 2x its own threshold (haversine distance), transferring the minimum of what's needed and what's spare |

This is real statistics, not an LLM guessing a number — every score and forecast is reproducible and auditable from the underlying daily logs.

## Repo structure

```
api/            FastAPI app: routers (CRUD + orchestration), db/ (Firestore or
                local-JSON repository, swappable via DB_BACKEND), services/
                (speech, swappable via USE_REAL_SPEECH_APIS), models/
                (Pydantic schemas - the 5-collection contract)
ml/             forecaster.py, scorer.py, recommender.py - pure functions, unit
                tested in ml/tests/, no Firestore/Gemini imports
gemini/         client.py + summarizer.py + alert_drafter.py + incident_tagger.py
data/seed/      constants.py (fictional Raighar District), generate_synthetic_data.py
                (90 days x 15 centres, seeded/reproducible), seed.py (loads it
                into whichever DB_BACKEND is active)
frontend/admin/ District dashboard: map, alerts feed, redistribution panel,
                per-centre drill-down with trend charts, English/Hindi/Odia toggle
frontend/staff/ Mobile intake PWA: daily log form, voice/text incident report
render.yaml     Render.com Blueprint for the backend (see "Deploying" below)
firebase.json   Firebase Hosting config (admin + staff as separate hosting targets)
```

A judge reading this repo should start at `ml/` (the actual algorithms, fully isolated and tested), then `gemini/` (to see the LLM boundary enforced in code, not just in docs), then `api/routers/orchestration.py` (how they're wired together).

## Local setup

### Backend

Requires Python 3.12+ (3.13/3.14 also work, but some scientific-package wheels lag new Python releases - if `pip install` tries to compile from source, use 3.12).

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
cp .env.example .env            # defaults to DB_BACKEND=local - no GCP needed yet
```

Generate the synthetic district (15 PHCs/CHCs, 90 days of logs) and seed the local store:

```bash
python -m data.seed.generate_synthetic_data
python -m data.seed.seed
```

Run the API:

```bash
uvicorn api.main:app --reload --port 8000
```

Run the tests (ML pure-function tests, Gemini prompt-contract tests with a fake client, API/router tests):

```bash
pytest
```

### Frontend

Each app is independent:

```bash
cd frontend/admin && npm install && npm run dev   # http://localhost:5173
cd frontend/staff && npm install && npm run dev    # http://localhost:5174
```

Both dev servers proxy `/api` to `http://127.0.0.1:8000` (see each `vite.config.ts`) - no env vars needed locally.

## Environment variables

| Variable | Where | Default | Notes |
|---|---|---|---|
| `DB_BACKEND` | backend `.env` | `local` | `local` = JSON file, no GCP; `firestore` = real GCP Firestore |
| `GOOGLE_CLOUD_PROJECT` | backend `.env` | - | required when `DB_BACKEND=firestore` |
| `GOOGLE_APPLICATION_CREDENTIALS` | backend `.env` | - | optional; ADC via `gcloud auth application-default login` (local dev) or a service-account JSON (deployed backend) — see "Switching to Firestore" |
| `GEMINI_API_KEY` | backend `.env` | - | from Google AI Studio; without it, Gemini calls fall back gracefully |
| `GEMINI_MODEL` | backend `.env` | `gemini-2.0-flash` | |
| `USE_REAL_SPEECH_APIS` | backend `.env` | `false` | `true` requires Speech-to-Text + Translation enabled on the project |
| `CORS_ALLOW_ORIGINS` | backend `.env` | `["http://localhost:5173","http://localhost:5174"]` | JSON array of exact origins; add your Firebase Hosting URLs for production |
| `VITE_API_BASE_URL` | each `frontend/*/.env.production.local` | unset (dev proxy) | set for production builds to the Render backend URL |

## What's mocked vs. real

- **Storage**: `DB_BACKEND=local` (default) writes to `local_data/db.json` so the whole stack runs with zero GCP setup — and the same file is baked into the Docker image at build time (see `Dockerfile`), so the deployed Render backend works with zero database setup too. Flip to `firestore` with no code changes once you've done the Firestore setup below.
- **Speech-to-Text / Translation**: `MockSpeechService` (default) decodes uploaded bytes as UTF-8 text and translates a handful of canned Hindi/Odia PHC phrases, so the voice flow is fully demoable without credentials. `RealSpeechService` (same interface, `USE_REAL_SPEECH_APIS=true`) calls actual Cloud Speech-to-Text + Translation - no frontend changes needed to switch.
- **Gemini**: real calls if `GEMINI_API_KEY` is set; templated fallbacks otherwise. The numeric ML pipeline never depends on Gemini being configured.

## Switching to Firestore

`DB_BACKEND` is the only thing that changes — `api/db/repository.py` picks the implementation at runtime, and both implement the same interface, so no calling code changes.

1. Create a Firestore database (Native mode) on the free Spark plan — via the [Firebase console](https://console.firebase.google.com) (no billing card required on Spark), project `swasthyasetu-hackathon`.
2. Auth, pick one:
   - **Local dev**: `gcloud auth application-default login`, leave `GOOGLE_APPLICATION_CREDENTIALS` unset.
   - **Deployed backend (Render)**: download a service-account JSON (GCP Console → IAM & Admin → Service Accounts → a key with the "Cloud Datastore User" role), upload it as a Render **Secret File**, and set `GOOGLE_APPLICATION_CREDENTIALS` to its mounted path.
3. Set `DB_BACKEND=firestore` and `GOOGLE_CLOUD_PROJECT=swasthyasetu-hackathon`.
4. Load the same synthetic dataset into Firestore (this *is* the migration script — it's backend-agnostic, so it just writes to whichever backend is active):
   ```bash
   python -m data.seed.generate_synthetic_data
   DB_BACKEND=firestore GOOGLE_CLOUD_PROJECT=swasthyasetu-hackathon python -m data.seed.seed
   ```
5. Confirm it worked: `GET /health` returns `document_counts` per collection, sourced live from whichever backend is active.

## Enabling real Speech-to-Text / Translation

Mocked by default (`USE_REAL_SPEECH_APIS=false`) so the voice flow is demoable with zero GCP setup. Once GCP credits/billing are available:

```bash
gcloud services enable speech.googleapis.com translate.googleapis.com --project swasthyasetu-hackathon
```

Set `USE_REAL_SPEECH_APIS=true` (and Firestore-style auth as above, since the real Speech/Translate clients need the same credentials) — `api/services/real_speech_service.py` implements the same interface as the mock, so no frontend or router changes are needed.

## Deploying (free tier: Firebase Hosting + Render.com)

### 1. Backend → Render.com

1. Create a free account at [render.com](https://render.com) (GitHub sign-in is simplest).
2. **New → Blueprint**, connect this GitHub repo — Render reads `render.yaml` from the repo root and provisions the `swasthyasetu-api` web service automatically.
3. Render will prompt for the two secrets marked `sync: false` in `render.yaml`: `GEMINI_API_KEY` (from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)) and `GOOGLE_APPLICATION_CREDENTIALS` (leave blank while `DB_BACKEND=local`).
4. Deploy. Render builds the Dockerfile (which bakes in the seeded demo dataset) and starts the service — note the deployed URL, e.g. `https://swasthyasetu-api.onrender.com`.
5. Confirm it's healthy:
   ```bash
   curl https://swasthyasetu-api.onrender.com/health
   ```
   Expect `{"status":"ok","db_backend":"local","document_counts":{...}}`.

Note: Render's free tier spins the service down after 15 minutes of inactivity and takes ~30-60s to cold-start on the next request — worth knowing before a live demo (hit `/health` a minute before presenting).

### 2. Frontends → Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
```

Firebase site IDs must be globally unique — if `swasthyasetu-admin` / `swasthyasetu-staff` are taken, pick your own and update `.firebaserc` (`targets.swasthyasetu-hackathon.hosting`) to match.

```bash
firebase hosting:sites:create swasthyasetu-admin
firebase hosting:sites:create swasthyasetu-staff
```

Point each frontend at the deployed Render URL and build:

```bash
echo "VITE_API_BASE_URL=https://swasthyasetu-api.onrender.com" > frontend/admin/.env.production.local
echo "VITE_API_BASE_URL=https://swasthyasetu-api.onrender.com" > frontend/staff/.env.production.local

(cd frontend/admin && npm run build)
(cd frontend/staff && npm run build)

firebase deploy --only hosting
```

Then go back to Render and set `CORS_ALLOW_ORIGINS` on the `swasthyasetu-api` service to the exact deployed URLs (see `render.yaml` for the expected format), so the browser apps are allowed to call the API.

Deployed URLs will look like:
- Admin dashboard: `https://swasthyasetu-admin.web.app`
- Staff intake app: `https://swasthyasetu-staff.web.app`

(or `https://<your-site-id>.web.app` / `.firebaseapp.com` if you picked different site IDs.)

### Post-shortlisting upgrade path

Once GCP credits are available, the same Dockerfile deploys to Cloud Run with `DB_BACKEND=firestore` and real Speech-to-Text/Translation — no application code changes, only environment variables and infra config, since every backend swap point (`db/repository.py`, `services/speech_service.py`) is an interface, not a hardcoded call.

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Backend framework | FastAPI + Pydantic | Async-friendly, automatic OpenAPI docs, and Pydantic gives us one schema definition shared by validation, serialization, and the API contract |
| ML | statsmodels (Holt-Winters / exponential smoothing), scipy, numpy, pandas | Battle-tested statistical forecasting instead of hand-rolled math or an LLM guessing numbers |
| LLM layer | Gemini API (`google-genai`, AI Studio key) | Free tier, no billing required, and a clean separation from the numeric pipeline (see "Gemini separation") |
| Database | Firestore (Spark plan) / local JSON | Firestore free tier needs no billing card; local JSON keeps zero-GCP local dev and CI fast |
| Speech/Translation | Cloud Speech-to-Text + Translation (mockable) | Regional-language voice intake for staff who may not be comfortable typing in English |
| Frontend | React 19 + Vite + TypeScript | Fast dev server, small bundles, strong typing across two independent apps sharing no runtime code |
| Styling | Tailwind CSS 4 | Rapid UI iteration during a hackathon timeline without a component library dependency |
| Charts | Recharts | Trend charts for per-centre drill-down (stock/footfall over time) |
| Hosting (frontend) | Firebase Hosting (Spark/free plan) | Free, global CDN, multi-site support (admin + staff as separate targets) out of the box |
| Hosting (backend) | Render.com (free tier) | Free Docker hosting with zero GCP billing setup, using the same Dockerfile Cloud Run would use later |
| Containerization | Docker | Identical image runs on Render now and Cloud Run later — no re-packaging for the post-hackathon upgrade |

## Key API endpoints

- `GET/POST /centres`, `/stock-items`, `/daily-logs`, `/alerts`, `/recommendations` - CRUD
- `PATCH /alerts/{id}/resolve`, `/recommendations/{id}/approve|reject`
- `POST /incidents/text`, `POST /incidents/voice` - staff incident intake (translate -> Gemini tag -> Alert)
- `POST /orchestration/run?language=English` - runs forecast -> score -> recommend -> Gemini summarize/draft for the whole district in one call; this is what the admin dashboard calls on load and on "Refresh Analysis"
- `GET /health` - backend + DB connectivity check, returns per-collection document counts

## Screenshots

_TODO: add screenshots here before submission —_
- Admin dashboard: district map + health scores
- Admin dashboard: alerts feed
- Admin dashboard: redistribution panel
- Admin dashboard: per-centre drill-down with trend chart
- Staff app: daily log form
- Staff app: voice incident report flow
