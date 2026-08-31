"""Normalization layer. Implement transform_record()."""


def transform_record(rec: dict) -> dict:
    """Convert one raw remittance record to the normalized schema.

    Required output keys:
    * remit_id: str
    * claim_id: str
    * amount_billed: float (USD)
    * amount_paid: float (USD)
    * reason: str
    * department: str
    * service_date: str (YYYY-MM-DD)

    Where the feed leaves the right handling unclear, the call is
    yours — record the reasoning in DECISIONS.md.
    """
    # TODO: implement me
    raise NotImplementedError
