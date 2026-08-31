# Take-Home (2-3 hrs) – Product Engineer (Backend-Leaning)

**Objective:** Complete the normalization layer of a claims-remittance ingestion service, design its claim and summary APIs, and surface the summary in a small provided dashboard.

This is a product engineering exercise: the dashboard has an end user. Part of your job is deciding who that is and building for them.

## Provided

* A working **FastAPI** scaffold (`app/`) with the missing pieces marked `TODO`.
* Synthetic input feed `data/sample_remittance.json`, already loaded off disk for you. The feed reflects real-world remittance behavior and is not perfectly clean.
* Database connections wired up in `app/db.py` — a MongoDB handle and a SQLAlchemy engine, both ready to use. You pick one; you write the reads and writes.
* `pytest` tests (currently **failing**) that validate the normalized schema, plus a shell in `tests/test_api.py` for the endpoint tests you write.
* A small **React dashboard** (`frontend/`) that renders the normalized remittance feed in a table, and one `TODO` panel waiting for your summary endpoint.

## Your Tasks

1. **Implement `transform_record()`** in `app/transform.py` so the provided tests pass.
2. **Persist the normalized feed** — fill in `store_remits()` and `fetch_remits()` in `app/db.py`. MongoDB or SQL, your call; the connections are already wired in `app/db.py`. This lights up `GET /remits` and the dashboard table.
3. **Design and implement `GET /claims`** in `app/main.py` — one entry per claim, read from your store. The shape is yours; document judgment calls in `DECISIONS.md`.
4. **Design and implement `GET /summary`** on top of your claim model. The shape is yours.
5. **Fill in the `TODO` panel** in `frontend/src/App.tsx` to render your summary (Recharts is installed).
6. **Fill in `tests/test_api.py`** — the stubs are skipped; unskip the ones you cover. We read what you chose to assert, not how many tests there are.
7. **Complete `DECISIONS.md`** (≤1 page). The required sections are in the file.

Use AI tools freely — we do. We will discuss your decisions, including your AI usage, at the onsite.

## Running locally

```bash
# backend
uv venv
uv pip install -r requirements.txt
uv run uvicorn app.main:app --reload        # API on :8000
uv run pytest                               # should pass once transform_record is implemented

# frontend
cd frontend
npm install
npm run dev                          # dashboard on :5173, proxies /api to :8000
```

## Persistence (required — pick one)

The service has to survive a restart, so the normalized feed goes in a real
store. Keeping it in a module-level list is not an answer.

**Which** store is up to you: use whichever of these you already know. We are
not grading the choice, we are grading what you say about it in
`DECISIONS.md` — including what you would have picked with more time.

`app/db.py` already holds the connection wiring, so you should not have to
write any. It gives you two handles, both lazy — nothing connects until you
issue a command, so the app boots and `pytest` passes with no database up:

```python
from .db import mongo, sql       # MongoDB Database, SQLAlchemy Engine

mongo().claims.insert_many(docs)         # MongoDB
with sql().begin() as conn:              # SQL
    conn.execute(text("select 1"))
```

Check a connection before you build on it — each returns `True` or raises
the driver's own error:

```bash
uv run python -c "from app.db import ping_sql; print(ping_sql())"
uv run python -c "from app.db import ping_mongo; print(ping_mongo())"
```

Defaults are overridable by env var: `DATABASE_URL` (default
`sqlite:///denials.db`), `MONGO_URL`, `MONGO_DB`.

* **SQLite** via `sqlalchemy>=2.0`. No server, no container — the driver
  ships with Python, and `sql()` is pointed at a local file already.
* **MongoDB** via `pymongo>=4.9`. Needs a running `mongod`:

  ```bash
  docker run -d --name mongodb -p 27017:27017 mongo:latest || nerdctl run -d --name mongodb -p 27017:27017 mongo:latest
  ```

  ```text
  mongodb://localhost:27017/denials
  ```

If you want to use MongoDB and need a container engine locally, we'd recommend [Rancher Desktop](https://rancherdesktop.io/). It's free and will work out of the box with the commands above.

Whichever you pick, `pytest` must still pass. If you use MongoDB, we will assume
the database is running and use the default connection string mentioned above.
`tests/test_transform.py` covers `transform_record()`, which is pure — do not
make it depend on a live store. `tests/test_api.py` is the shell for the
endpoint tests: one health check that passes today, skipped stubs for the
rest.

## Submission

* Push to a Git repo or share a zip.
* Make sure `uv run pytest` passes and both servers start.
* `DECISIONS.md` is weighted as heavily as the code.
