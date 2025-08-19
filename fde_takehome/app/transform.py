"""Add your business‑logic here."""

from datetime import datetime

def transform_record(rec: dict) -> dict:
    """Convert raw remittance JSON to normalized claim schema.

    Required output keys:
    * claim_id: str (Cxxxxx)
    * amount: float (USD)
    * denial_reason: str
    * department: str
    * service_date: YYYY‑MM‑DD
    """
    # TODO: implement me
    # Example (delete once implemented):
    return {
        "claim_id": rec["claim_id"],
        "amount": float(rec["amount"]),
        "denial_reason": rec["issue"],
        "department": rec["department"],
        "service_date": rec["service_date"].split("T")[0] if "T" in rec["service_date"] else rec["service_date"]
    }
