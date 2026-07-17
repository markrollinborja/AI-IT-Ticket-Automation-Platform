"""
Shared pytest fixtures.

This file has two jobs:

1. Provide safe, dummy values for the environment variables the app
   requires. Settings() fails fast on missing values (correct behavior
   for the real app), which means tests need *something* set for every
   required field, even tests that never touch Jira/Slack/OpenAI. These
   MUST be set before anything imports `app.main`, because that import
   chain builds the Settings() singleton immediately - so this block has
   to run before any `app.*` import below.

2. Provide a real Postgres-backed test database, isolated from your dev
   database. Each test runs inside its own transaction that gets rolled
   back afterward, so tests never leave data behind or interfere with
   each other. We test against real Postgres (not SQLite) so the test
   suite catches the same dialect-specific issues production would hit.
"""

import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/ai_ticket_automation_test",
)
os.environ.setdefault("JIRA_BASE_URL", "https://example.atlassian.net")
os.environ.setdefault("JIRA_EMAIL", "test@example.com")
os.environ.setdefault("JIRA_API_TOKEN", "test-token")
os.environ.setdefault("JIRA_PROJECT_KEY", "TEST")
os.environ.setdefault("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/test")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base

# Importing these registers every table on Base.metadata. Without this,
# Base.metadata.create_all() below would create zero tables - SQLAlchemy
# only knows about a model once its module has been imported somewhere.
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.ticket import Ticket  # noqa: F401
from app.models.workflow_run import WorkflowRun  # noqa: F401


def _ensure_test_database_exists(database_url: str) -> None:
    """
    Create the test database if it doesn't exist yet.

    This makes the suite self-provisioning: a new developer only needs
    Postgres running (`docker compose up -d db`), not a manually created
    test database. You can't CREATE DATABASE while connected to the
    database you're creating, so this connects to the default
    "postgres" maintenance database instead.
    """
    db_name = database_url.rsplit("/", 1)[-1]
    maintenance_url = database_url.rsplit("/", 1)[0] + "/postgres"

    conn = psycopg2.connect(maintenance_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cur.fetchone() is None:
                cur.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        conn.close()


@pytest.fixture(scope="session")
def db_engine():
    """Session-scoped engine bound to the test database; tables created once."""
    database_url = os.environ["DATABASE_URL"]
    _ensure_test_database_exists(database_url)

    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """
    A database session scoped to a single test, wrapped in a transaction
    that gets rolled back afterward. This is what keeps tests isolated
    from each other without needing to truncate tables between runs.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = session_factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """A FastAPI TestClient wired to the transactional test session instead
    of the app's real database connection, via dependency override."""
    from fastapi.testclient import TestClient

    from app.db.session import get_db
    from app.main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
