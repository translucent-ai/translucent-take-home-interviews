from fastapi import FastAPI
from .transform import transform_record
import json, pathlib

app = FastAPI()

@app.on_event("startup")
def ingest():
    sample_path = pathlib.Path(__file__).parent.parent / "data" / "sample_remittance.json"
    records = json.loads(sample_path.read_text())
    global normalized
    normalized = [transform_record(r) for r in records]

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/claims")
def claims():
    return normalized
