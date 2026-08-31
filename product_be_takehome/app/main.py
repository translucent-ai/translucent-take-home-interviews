import json
import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .db import fetch_remits, store_remits
from .transform import transform_record

app = FastAPI(title="Denials Ingestion Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "sample_remittance.json"


def load_raw_records() -> list[dict]:
    """Provided. The feed exactly as it sits on disk — nothing to do here."""
    return json.loads(DATA_PATH.read_text())


@app.on_event("startup")
def ingest() -> None:
    """Load, normalize, persist.

    The load is given and the normalize is `transform_record()`. The write
    is yours: the service must survive a restart, so the feed has to land
    in a real store. See `app/db.py`.
    """
    try:
        records = [transform_record(r) for r in load_raw_records()]
        store_remits(records)
    except NotImplementedError:
        # App still boots; /remits explains what's missing.
        pass


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/remits")
def remits() -> list[dict]:
    """The normalized feed, straight from your store. Backs the table in
    the dashboard, so it is the fastest way to see your work render."""
    try:
        rows = fetch_remits()
    except NotImplementedError:
        raise HTTPException(503, "persistence is not implemented yet — see app/db.py")
    if not rows:
        raise HTTPException(
            503,
            "no remits stored — implement transform_record() and the read/write "
            "pair in app/db.py, then restart to re-run ingest()",
        )
    return rows


@app.get("/claims")
def claims():
    """One entry per claim. The feed is remit-level; what a claim's
    status and amounts are is yours to decide. The shape is yours.

    Read from the store, not from a module-level list — see `app/db.py`."""
    # TODO: implement me
    raise NotImplementedError


@app.get("/summary")
def summary():
    """Powers the dashboard's summary panel, on top of your claim model.
    Decide who reads it and what they need from it."""
    # TODO: implement me
    raise NotImplementedError
