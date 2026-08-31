# Take-Home (2-3 hrs) – Product Engineer (Backend-Leaning)

**Objective:** Complete the normalization layer of a claims-remittance ingestion service, design its claim and summary APIs, and surface the summary in a small provided dashboard.

This is a product engineering exercise: the dashboard has an end user. Part of your job is deciding who that is and building for them.

## Provided

* A working **FastAPI** scaffold (`app/`) with the missing pieces marked `TODO`.
* Synthetic input feed `data/sample_remittance.json`. The feed reflects real-world remittance behavior and is not perfectly clean.
* `pytest` tests (currently **failing**) that validate the normalized schema.
* A small **React dashboard** (`frontend/`) that already renders the normalized remittance feed in a table. It has one `TODO` panel waiting for your summary endpoint.

## Your Tasks

1. **Implement `transform_record()`** in `app/transform.py` so the provided tests pass.
2. **Design and implement `GET /claims`** in `app/main.py` — one entry per claim. The shape is yours; document judgment calls in `DECISIONS.md`.
3. **Design and implement `GET /summary`** on top of your claim model. The shape is yours.
4. **Fill in the `TODO` panel** in `frontend/src/App.tsx` to render your summary (Recharts is installed).
5. **Complete `DECISIONS.md`** (≤1 page). The required sections are in the file.

Use AI tools freely — we do. We will discuss your decisions, including your AI usage, at the onsite.

## Running locally

```bash
# backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload        # API on :8000
pytest                               # should pass once transform_record is implemented

# frontend
cd frontend
npm install
npm run dev                          # dashboard on :5173, proxies /api to :8000
```

## Submission

* Email us a zip of the project (leave out `venv/` and `node_modules/`).
* Make sure `pytest` passes and both servers start.
* `DECISIONS.md` is weighted as heavily as the code.
