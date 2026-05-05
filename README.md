# auto-man

Autonomous Affiliate Growth Engine built with FastAPI.

This project helps you:
- Fetch and store trends
- Create products and score profitability
- Generate AI marketing content
- Track content performance and decisions
- Scale winning content with variants
- Manage affiliate links and click analytics

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- SQLite (local dev)
- Uvicorn

## Project Structure

```text
app/
  main.py
  core/
  models/
  schemas/
  services/
  routers/
```

## Local Setup

1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the API

```bash
uvicorn app.main:app --reload
```

4. Open docs

`http://127.0.0.1:8000/docs`

## Database

Local database uses:

`sqlite+aiosqlite:///./test.db`

Tables are auto-created on startup for local MVP use.

## Core Routes

- `POST /trends/fetch`
- `GET /trends`
- `POST /products/create`
- `GET /products`
- `POST /content/generate/{product_id}`
- `GET /content/{product_id}`
- `GET /content/export/{content_id}?platform=tiktok`
- `GET /content/performance-status/{content_id}`
- `GET /content/decision/{content_id}`
- `POST /performance/log`
- `GET /performance/{content_id}`
- `POST /automation/run`
- `POST /scaling/run`
- `POST /affiliate/create`
- `GET /affiliate/{product_id}`
- `GET /track/{tracking_code}`
- `GET /analytics/summary`
- `GET /analytics/report`
- `GET /health`

## Environment Variables (Optional)

- `OPENAI_API_KEY`
- `GOOGLE_TRENDS_ENABLED` (default: `true`)
- `APP_BASE_URL` (default: `http://localhost:8000`)

