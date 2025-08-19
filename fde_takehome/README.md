# Take‑Home (2‑3 hrs) – Forward Deployed Engineer

**Objective:** Complete the normalization layer of a claims‑remittance ingestion service.

## Provided

* A fully working **FastAPI** scaffold (`app/`) with one missing function.
* Synthetic input feed `data/sample_remittance.json`.
* `pytest` tests (currently **failing**) that validate the normalized schema.

## Your Tasks

1. Implement `transform_record()` in `app/transform.py` so tests pass.
2. Update `README_design.md` with the trade‑offs you’d consider to productionize this (batch vs. stream, idempotency, schema evolution).

## Running locally

```bash
docker compose up --build       # API should start on :8000
pytest                           # all tests should pass
```

Expect ~2 hours of coding plus 20‑30 min for the design doc.

---
