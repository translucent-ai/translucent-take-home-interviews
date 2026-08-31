"""API-level tests — a shell. The assertions are yours to write.

`tests/test_transform.py` covers the pure normalization step and needs no
database. These are the other half: they boot the app, which runs
`ingest()`, which writes to whatever store you picked. So they need that
store reachable — a file for SQLite, a running container for MongoDB.

Everything below except the health check is skipped, so a fresh clone is
green. Delete the skip marker as you implement each piece. We care more
about what you chose to assert than about how many tests there are.
"""

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


@pytest.fixture
def client():
    """A client whose startup has run, so `ingest()` has populated the store."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def throwaway_sqlite(tmp_path, monkeypatch):
    """Provided, for the SQL path: point the engine at a per-test file so
    these tests never scribble on the database you develop against.

    Request it before `client`. Mongo users want the equivalent — a scratch
    database name — or a container they do not mind truncating.
    """
    monkeypatch.setattr(db, "DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    db.sql.cache_clear()
    yield
    db.sql.cache_clear()


def test_healthz(client):
    """The one test that passes on a fresh clone. Proves the app boots."""
    assert client.get("/healthz").json() == {"status": "ok"}


@pytest.mark.skip(reason="TODO: unskip once store_remits/fetch_remits are done")
def test_remits_round_trips_through_the_store(throwaway_sqlite, client):
    """Whatever `ingest()` wrote, `/remits` should read back.

    Worth deciding: does every raw record survive the trip, and if not,
    which ones do you drop and can you defend it?
    """
    raise NotImplementedError


@pytest.mark.skip(reason="TODO: unskip once /claims is implemented")
def test_claims_are_one_row_per_claim(client):
    """The feed is remit-level and `/claims` is not. Assert the collapse:
    claim count, and what happened to a claim with several remits."""
    raise NotImplementedError


@pytest.mark.skip(reason="TODO: unskip once /summary is implemented")
def test_summary_shape(client):
    """Pin the contract your dashboard panel depends on. If a number here
    is wrong, the person reading the dashboard makes a bad call — so assert
    the arithmetic, not just the keys."""
    raise NotImplementedError


@pytest.mark.skip(reason="TODO: your call — is an empty store a 200 or a 503?")
def test_endpoints_when_the_store_is_empty(client):
    """Decide what these endpoints do with nothing behind them, then say so
    here. There is no single right answer; there is a wrong one, which is
    for it to be an accident."""
    raise NotImplementedError
