# Starbucks AI Financial Analyst

**SEC Filing-Based Financial Performance Assistant** — an educational advisory-style AI web application analyzing Starbucks SEC financial facts.

## Features
- Data-backed AI conversation with loading indicator and automatic chat persistence
- Firestore `data` record CRUD, verified source metadata, Pydantic validation
- Firestore `conversations` save, list, load full messages, delete
- Financial summary, trends, operating margin, revenue line chart, JSON export and dark-mode toggle
- FastAPI Swagger at `/docs`; vanilla HTML/CSS/JavaScript frontend

## Data provenance and limitations
- `data/starbucks_2019_2025.csv`: **112 records** (FY2019–FY2025; 7 fiscal years × 4 quarters × Revenue, Operating Income, Net Income Attributable to Starbucks, Total Assets).
- Generated from the **user-uploaded** SEC Company Facts JSON (`data/sec_companyfacts_sbux_original.json`) using `scripts/extract_sec.py`, without network fetching. Reproduce: `python scripts/extract_sec.py data/sec_companyfacts_sbux_original.json --out data/starbucks_2019_2025.csv`.
- FY2024–FY2025 32 data values also matched separately uploaded company reports, with no discrepancies.
- Data amounts: USD **millions**. Revenue/Operating Income/Net Income are discrete fiscal-quarter flows; Total Assets is a quarter-end snapshot.
- Fiscal Q4 income amounts calculated as the fiscal year's annual amount minus fiscal Q3 year-to-date (9-month) amount. Source accession numbers, filing dates, calculation notes, and GAAP tags preserved.
- This is a research prototype, **not financial/investment advice**. Summary injection gives the AI aggregates and latest-quarter statistics, not every raw observation; questions about unavailable precise historical values should be qualified.
- Public SEC disclosures can be revised; re-validation against source filings is needed for production-quality use.

## Stack
Python 3.10+, FastAPI, Uvicorn, Pydantic, Firebase Admin / Firestore, OpenAI API, python-dotenv; vanilla HTML/CSS/JS; Render backend, Vercel frontend.

## Local setup

```bash
cd backend
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
cp .env.example .env  # Windows: copy .env.example .env
# add secrets locally, never commit .env
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

In a second terminal, from `backend` with the same venv and environment:

```bash
python seed.py ../data/starbucks_2019_2025.csv
```

This will idempotently upsert 112 records to `data`. The local frontend can be served via `python -m http.server 3000 --directory frontend` **from the project root**. Configure `frontend/config.js` for the local backend URL (default http://localhost:8000).

## Environment variables (secrets only in backend)
| Variable | Where | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | Render + backend `.env` | Private GPT API key; billed separately |
| `OPENAI_MODEL` | Backend | Defaults to `gpt-4o-mini` |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Render + backend | JSON service account, optionally base64 encoded |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | Local backend alternative | Absolute path to service account JSON file |
| `ALLOWED_ORIGINS` | Backend | Comma-separated trusted frontend origins, no trailing slash |
| `API_BASE_URL` | Vercel build time | HTTPS Render server base URL; generated into public `config.js` (not a secret) |

## Cloud deployment
1. Create Firebase Firestore database and least-privileged service account credential. Add Firebase credentials to Render **environment**, not code.
2. Push repository to GitHub. Deploy Render Python Web Service using `backend` root, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (or use root `backend/render.yaml` blueprint).
3. Set backend environment variables and `ALLOWED_ORIGINS=https://YOUR-VERCEL-APP.vercel.app`.
4. Seed 112 rows using local `python backend/seed.py data/starbucks_2019_2025.csv` after supplying Firebase credentials locally.
5. Deploy frontend from repository **root** to Vercel. Framework preset: **Other**. Set `API_BASE_URL=https://YOUR-RENDER-URL.onrender.com`; `vercel.json` runs a build that generates the frontend configuration. Output is `frontend`.
6. Visit backend `/docs` and frontend; test edit/delete, new chat, saved conversation loading. Render cold starts can delay initial requests.

## API specification
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/data` | Create validated record |
| GET | `/api/data` | List records |
| PUT | `/api/data/{id}` | Update record |
| DELETE | `/api/data/{id}` | Delete record |
| GET | `/api/data/summary` | Aggregate financial summary |
| POST | `/api/conversations` | Save conversation |
| GET | `/api/conversations` | List saved conversations (includes messages) |
| GET | `/api/conversations/{id}` | Load full conversation messages |
| DELETE | `/api/conversations/{id}` | Delete conversation |
| POST | `/api/chat` | GPT chat + automated conversation save |

## SECURITY WARNING
This coursework prototype does **not implement authentication or per-user Firestore isolation**. Do not publish unrestricted write endpoints in a real public production application, and do not store personal/sensitive data. Before public launch, introduce auth and rules/rate limiting (or an authenticated backend gateway), request quotas and spending caps. Never put OpenAI or service account keys in client-side code.

## Deployment URLs (fill after successful deployment)
- Frontend: **not deployed**
- Backend API: **not deployed**
- Swagger: **not deployed**

## Submission screenshots (capture after deployment)
- [ ] AI conversation including financial context and response
- [ ] Data manager showing one CREATE/EDIT/DELETE action
- [ ] Conversation history with successful loading

## Local checks
`python -m pytest tests -q` from project root after installing `pytest` for tests. Test actual connected API only once Firebase and OpenAI are configured; no external credentials were available when building this starter project.
