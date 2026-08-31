"""These tests cover schema normalization only; they are not a complete
spec of the feed."""

import json
import pathlib

from app.transform import transform_record

RECORDS = json.loads(
    (pathlib.Path(__file__).parent.parent / "data" / "sample_remittance.json").read_text()
)
BY_REMIT = {r["remit_id"]: r for r in RECORDS}

EXPECTED_KEYS = {
    "remit_id",
    "claim_id",
    "amount_billed",
    "amount_paid",
    "reason",
    "department",
    "service_date",
}


def test_clean_record_schema():
    out = transform_record(BY_REMIT["R100001"])
    assert set(out.keys()) == EXPECTED_KEYS
    assert isinstance(out["amount_billed"], float)
    assert isinstance(out["amount_paid"], float)


def test_string_amounts_become_floats():
    out = transform_record(BY_REMIT["R100012"])
    assert out["amount_billed"] == 2450.0
    assert out["amount_paid"] == 0.0


def test_dates_normalize_to_iso():
    assert transform_record(BY_REMIT["R100012"])["service_date"] == "2025-06-10"


def test_department_casing_is_consistent():
    canonical = transform_record(BY_REMIT["R100002"])["department"]
    assert transform_record(BY_REMIT["R100011"])["department"] == canonical
