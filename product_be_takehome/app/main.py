import json
import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .transform import transform_record

app = FastAPI(title="Denials Ingestion Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "sample_remittance.json"
normalized: list[dict] = []


@app.on_event("startup")
def ingest() -> None:
    records = json.loads(DATA_PATH.read_text())
    normalized.clear()
    try:
        normalized.extend(transform_record(r) for r in records)
    except NotImplementedError:
        # App still boots; /remits explains what's missing.
        normalized.clear()


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/remits")
def remits() -> list[dict]:
    if not normalized:
        raise HTTPException(503, "transform_record is not implemented yet")
    return normalized


@app.get("/claims")
def claims():
    """One entry per claim. The feed is remit-level; what a claim's
    status and amounts are is yours to decide. The shape is yours."""
    # TODO: implement me
    raise NotImplementedError


@app.get("/summary")
def summary():
    """Powers the dashboard's summary panel, on top of your claim model.
    Decide who reads it and what they need from it."""
    # TODO: implement me
    raise NotImplementedError
