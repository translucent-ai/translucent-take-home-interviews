"""Database wiring, plus the two functions you have to write.

Persisting the feed is required — the service has to survive a restart,
so keeping records in a module-level list is not an answer. Pick MongoDB
or SQL, whichever you know better; the choice itself is not graded, but
your reasoning in DECISIONS.md is.

The connections are done for you. `mongo()` and `sql()` below are ready
to use, and neither connects at import time, so the app boots and
`pytest` passes with no database running.

Overridable via env vars:

    MONGO_URL     default: mongodb://localhost:27017/denials
    MONGO_DB      default: denials
    DATABASE_URL  default: sqlite:///denials.db (a file in the repo root)
"""

import os
from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database
from sqlalchemy import Engine, create_engine, text

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/denials")
MONGO_DB = os.getenv("MONGO_DB", "denials")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///denials.db")


@lru_cache(maxsize=1)
def mongo() -> Database:
    """The MongoDB database handle. Needs `docker compose up -d`.

        from .db import mongo
        mongo().claims.insert_many(docs)

    Fails in ~3s rather than the 30s default when nothing is listening,
    so a forgotten container is obvious instead of looking like a hang.
    """
    client: MongoClient = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
    return client[MONGO_DB]


@lru_cache(maxsize=1)
def sql() -> Engine:
    """The SQLAlchemy engine. SQLite by default — no server needed.

        from sqlalchemy import text
        from .db import sql
        with sql().begin() as conn:
            conn.execute(text("select 1"))

    `check_same_thread` is off because FastAPI runs sync endpoints in a
    threadpool, and SQLite otherwise refuses a connection reused across
    threads. Harmless here; revisit it under real concurrency.

    Stay on a file URL. `sqlite:///:memory:` gives each thread its own
    empty database, so a startup write vanishes before a request reads it.
    """
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    return create_engine(DATABASE_URL, connect_args=connect_args)


def ping_mongo() -> bool:
    """True if MongoDB answers. Raises the driver error if it does not."""
    mongo().client.admin.command("ping")
    return True


def ping_sql() -> bool:
    """True if the SQL engine connects. Raises the driver error if not."""
    with sql().connect() as conn:
        conn.execute(text("select 1"))
    return True


def store_remits(records: list[dict]) -> None:
    """Write the normalized feed to your store. Called once, at startup.

    Startup runs on every reload, so this needs to be safe to run twice —
    decide whether that means replacing the collection/table, upserting on
    `remit_id`, or something else, and say why in DECISIONS.md.
    """
    # TODO: implement me
    raise NotImplementedError


def fetch_remits() -> list[dict]:
    """Read the normalized feed back out. Backs `GET /remits`.

    Return the same shape `transform_record()` produces — the dashboard
    table and your `/claims` work both build on it. Mongo hands back an
    `_id` you did not ask for; SQL hands back `Row` objects, not dicts.
    """
    # TODO: implement me
    raise NotImplementedError
