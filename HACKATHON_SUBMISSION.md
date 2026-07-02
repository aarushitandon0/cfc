# SwasthyaSetu — Hackathon Submission Package

Working documents for the pitch deck, demo video script, and submission form
text. Not part of the application — feel free to delete or move out of the
repo once the submission is done (or keep it, it contains no secrets).

---

## Pitch deck — 12 slides

### Slide 1: Title
**SwasthyaSetu**
*A district health network that predicts stock-outs before they happen — in the language its own staff speak.*

Visual: district map graphic or a PHC exterior photo, logo/title overlay.

---

### Slide 2: The Problem
- District health officers overseeing PHCs/CHCs have **no real-time visibility** into medicine stock levels, footfall, or bed availability across their network.
- **Medicine stock-outs** are discovered only when a patient is turned away — not predicted in advance.
- **Doctor attendance is unpredictable** and under-monitored; overcrowding at one centre often coincides with spare capacity at a nearby one, with no mechanism to rebalance.
- Frontline staff — the people holding the actual data — report on paper or by phone call, in a language and format that doesn't reach a dashboard.

Visual: a simple "before" diagram — disconnected PHCs, a stock-out icon, a frustrated patient icon.

---

### Slide 3: Who it serves
- **PHC/CHC staff** → log daily intake in under a minute, report incidents by voice, in their own language.
- **District health officers** → one dashboard, every centre's health score, active alerts, redistribution suggestions.
- **Patients** → fewer stock-outs, less overcrowding, more predictable care.
- **MPs' offices / district administration** → a scalable, low-cost oversight model that can extend district → state.

Visual: the 4-step chain diagram from the README ("Who it serves").

---

### Slide 4: Solution overview + architecture
Explain in plain terms for a non-technical audience:
- Staff report daily numbers (or speak them) into a simple mobile app.
- Those numbers flow into a real statistics engine that predicts stock-outs and scores every centre's health.
- A district dashboard shows the whole network at a glance, with concrete suggestions ("send 40 units of ORS from Centre A to Centre B").
- 5 layers: staff intake → storage → ML pipeline → API → district dashboard.

Visual: the 5-layer architecture diagram (simplified version of the README's Mermaid diagram, redrawn as a clean flowchart).

---

### Slide 5: The AI/ML pipeline — real statistics, not guesswork
- **Forecaster**: exponential smoothing (Holt-Winters) predicts days-to-stockout per medicine and 7-day footfall per centre — the same class of method used in real inventory/demand forecasting systems.
- **Scorer**: a composite z-score across 4 metrics (stock, attendance, beds, test kits), benchmarked against district peers, mapped to a 0–100 health score.
- **Recommender**: a greedy nearest-neighbour matching algorithm pairs surplus centres with deficit centres by urgency and distance.
- **Every number is reproducible and auditable** from the underlying daily logs — nothing here is an LLM inventing a figure.

Visual: a simple chart mockup — a stockout countdown line, a health-score gauge, a "surplus → deficit" arrow between two centres on the map.

---

### Slide 6: Gemini's role — and its limit
- Gemini (Google AI Studio) is used **only** to explain, translate, and tag — never to compute.
- It turns a health score + z-score breakdown into a plain-language summary for a district officer, in their chosen language.
- It drafts alert sentences from an already-decided category/severity.
- It tags free-text incident notes (the one place it reads raw text, since no statistical model exists for that).
- **It never generates a forecast or a score.** This is enforced in code, not just policy — the function signatures only accept precomputed numbers, and tests assert on it.

Visual: a simple "boundary" diagram — ML pipeline box on the left computing numbers, an arrow crossing into a Gemini box on the right labeled "explains only," with a crossed-out arrow going backward labeled "never computes."

---

### Slide 7: Multilingual + voice intake
- District dashboard and staff app both support **English, Hindi, and Odia**, toggle-switchable at runtime.
- Staff can report incidents **by voice**, removing the barrier of typing on a phone in a second language.
- The voice path (Speech-to-Text → Translation → Gemini tagging) is demoable today via a mock service with identical behavior/interface to the real Cloud Speech-to-Text + Translation APIs — flipping one environment variable switches to the real APIs with no code changes, once GCP credits are available.
- Built for the reality of PHC staffing: regional-language-first, not English-first.

Visual: screenshot of the language toggle + the voice button on the staff app.

---

### Slide 8: Live demo
- Admin dashboard: district map with colour-coded health scores, alerts feed, redistribution panel.
- Staff app: daily log form, voice incident report.

Visual: 3–4 actual screenshots (insert after capturing from the deployed app) — district map, centre drill-down chart, redistribution panel, staff daily log form.

---

### Slide 9: Deployability — free today, GCP-native tomorrow
- **Today**: Firebase Hosting (frontends, free Spark plan) + Render.com (backend, free tier) — zero cost, zero billing card, deployed in under an hour.
- **Post-shortlisting**: the identical Docker image deploys to **Cloud Run**, storage flips to **Firestore**, voice flips to real **Cloud Speech-to-Text + Translation** — one environment variable each, no application code changes.
- Architecture was built swappable from day one: `DB_BACKEND` and `USE_REAL_SPEECH_APIS` are the only two switches between "hackathon demo" and "production GCP deployment."
- Scales district → state by adding centres to the same 5-collection schema — no architectural change required.

Visual: a simple "today vs. tomorrow" two-column comparison graphic (Render+Firebase vs. Cloud Run+Firestore+real Speech APIs), with an arrow showing "same Docker image."

---

### Slide 10: Impact potential
- This build's demo district (15 PHCs/CHCs, modeled on real Odisha PHC/CHC patterns) sees an estimated **~750 patient visits per day**, or **~270,000 per year**, across just one district.
- India has 700+ districts with multiple PHC/CHC networks each — the same 5-collection schema scales horizontally by simply adding centres.
- **One prevented stock-out** of a medicine like ORS or antimalarials, at a rural PHC with no same-day resupply option, is the difference between a treatable case and a referral (or worse) for a patient who may not be able to travel to a larger facility.
- Redistribution recommendations turn "Centre A ran out" + "Centre B has surplus" from a missed connection into a same-day, ranked, distance-aware action.

Visual: a simple stat callout slide — "15 centres · ~750 visits/day · 1 district" with an icon-based "prevented stock-out = treated patient" visual.

---

### Slide 11: Tech stack
| Layer | Technology |
|---|---|
| Backend | FastAPI, Pydantic, Python 3.12 |
| ML | statsmodels, scipy, numpy, pandas |
| LLM (explain/translate/tag only) | **Gemini API** (Google AI Studio) |
| Database | **Firestore** (Spark/free plan) / local JSON |
| Voice | **Cloud Speech-to-Text**, **Cloud Translation** (mockable) |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS 4, Recharts |
| Hosting | **Firebase Hosting** (frontends), Render.com → **Cloud Run** (backend) |
| Containerization | Docker |

Bold = Google Cloud / Firebase-native products.

Visual: the table above, or a logo grid grouped by layer.

---

### Slide 12: Ask + next steps
- **Ask**: a pilot in one district — access to PHC/CHC staff for a 2-week shadow period to validate the daily-intake workflow against real reporting habits.
- **What we need**: an introduction to a district health office willing to pilot, and GCP credits to move from the free tier to Firestore + real Speech-to-Text/Translation.
- **90-day success metrics**:
  - ≥90% of daily logs submitted on time across pilot centres.
  - At least one redistribution recommendation acted on per week.
  - Measurable reduction in stock-out incidents reported at pilot centres vs. the prior quarter.

Visual: simple 3-bullet "next 90 days" timeline graphic.

---

## Demo video script (4 minutes)

**Format**: spoken narration + on-screen action. Record screen at 1080p; keep
each screen segment on-camera for the full stated duration before cutting.

---

**[0:00–0:30] Problem statement — no screen, or a PHC photo/stock image**

> "In district health networks across India, PHCs and CHCs run out of essential
> medicines with almost no warning. A district officer might oversee fifteen
> centres, but has no way to see, in real time, which one is about to run out
> of ORS, which one has a doctor who's been absent for a week, or which nearby
> centre has spare stock that could have covered the gap. SwasthyaSetu closes
> that gap — with real statistical forecasting, not guesswork, and an intake
> flow built for the staff who actually hold the data."

---

**[0:30–1:00] Staff intake app — screen recording, staff PWA**

> "It starts with the staff app. A health worker opens today's log, confirms
> yesterday's stock levels, and reports today's footfall and bed occupancy —
> in under a minute."

Screen actions:
1. Open the staff app home screen.
2. Start the daily log form — show it prefilled with yesterday's stock levels.
3. Adjust one or two fields (stock count, footfall).
4. Tap the voice button to show the incident-report flow — speak a short mock incident note (or play a pre-recorded clip), show it get transcribed/translated.
5. Submit.

> "The voice path works even without live cloud credentials today — it's built
> on the same interface the real Speech-to-Text and Translation APIs use, so
> switching to the real thing later is a one-line config change."

---

**[1:00–2:00] Admin dashboard — district overview**

> "On the other end, the district health officer sees this instantly. Every
> centre is scored zero to a hundred, benchmarked against its peers — not an
> arbitrary number, but a composite z-score across stock availability, doctor
> attendance, bed availability, and test-kit availability."

Screen actions:
1. Open the admin dashboard.
2. Show the district map with colour-coded centre health scores.
3. Point out 2–3 flagged (low-scoring) centres.
4. Toggle the language switch (English → Hindi or Odia) to show multilingual support live.

---

**[2:00–2:45] Drill into a low-scoring centre**

> "Drilling into one flagged centre, we see exactly why it's underperforming —
> a stock-out forecast showing days remaining on each medicine, a footfall
> trend, and a plain-language summary written by Gemini — but Gemini didn't
> compute any of these numbers. It only explains numbers the statistics engine
> already produced."

Screen actions:
1. Click into the flagged centre's detail page.
2. Show the stock-out forecast chart (days-to-stockout per medicine).
3. Show the 7-day footfall forecast chart.
4. Show the AI-generated summary text, and (if visible) point out it references the same numbers just shown on screen.

---

**[2:45–3:15] Redistribution recommendations**

> "And because one centre's shortfall is often another centre's surplus, the
> system recommends exactly which centre should send how much of a medicine,
> ranked by urgency and distance — one click to approve."

Screen actions:
1. Open the redistribution panel.
2. Show a ranked list of recommendations (from-centre, to-centre, medicine, quantity, distance).
3. Click "Approve" on one recommendation, show its status update.

---

**[3:15–3:45] Alert generation**

> "Alerts surface automatically too — from a chronic stock-out pattern, an
> erratic attendance record, or a staff-reported incident — each with a
> severity and a plain-language message."

Screen actions:
1. Open the alerts feed.
2. Show 1–2 alerts with their severity badges.
3. Resolve one alert to show the workflow closing the loop.

---

**[3:45–4:00] Close**

> "SwasthyaSetu — real statistical ML for the forecast, Gemini only for the
> language, and an architecture that runs free today and scales to the full
> Google Cloud stack tomorrow."

Screen action: cut to the architecture/tech-stack slide, hold for the final few seconds.

---

## Submission form text

### "Explain your solution" (max 1000 characters — verified at 899)

```
SwasthyaSetu gives district health officers real-time visibility across PHC/CHC networks. Frontline staff log daily stock, footfall, and attendance via a mobile PWA — by voice or text, in English, Hindi, or Odia — feeding a statistical ML pipeline: exponential smoothing (statsmodels) for stock-out and footfall forecasts, z-score scoring for a 0-100 centre health score, and greedy geographic matching for medicine redistribution. Gemini (Google AI Studio) only explains, translates, and tags these precomputed numbers — it never generates a forecast or score. The dashboard surfaces flagged centres, ranked redistribution recommendations, and alerts. Deployed free on Firebase Hosting + Render.com today; one env-var flip moves storage to Firestore, voice to real Cloud Speech-to-Text/Translation, and hosting to Cloud Run once GCP credits arrive — GCP-native by design, demoable at zero cost now.
```

### "Technologies used" (max 1024 characters — verified at 912)

```
Backend: Python, FastAPI, Pydantic, Uvicorn. ML: statsmodels (Holt-Winters/exponential smoothing), scipy, numpy, pandas. AI: Gemini API (Google AI Studio) for explanation/translation/tagging only, via google-genai SDK. Database: Google Cloud Firestore (Spark/free plan), swappable with a local JSON store for zero-GCP dev. Voice/Language: Google Cloud Speech-to-Text, Google Cloud Translation API (mockable, same interface). Frontend: React 19, TypeScript, Vite, Tailwind CSS 4, Recharts, React Router, Axios. Hosting: Firebase Hosting (Spark/free plan, multi-site) for both frontends; Render.com (free tier) for the backend today, Google Cloud Run for the post-shortlisting upgrade — same Docker image for both. Testing: pytest (30 tests: ML pure-function tests, Gemini prompt-contract tests, API/router tests). Infra-as-config: Docker, render.yaml (Render Blueprint), firebase.json (multi-site Hosting config).
```
