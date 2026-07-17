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
from sqlalchemy import create_engine, event
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

    The tricky part: the app's own service layer calls `db.commit()` as
    part of normal operation (see ticket_persistence_service,
    workflow_run_service, audit_log_service). A plain "begin a
    transaction, roll it back at the end" setup breaks the moment app
    code commits, because that commit would end our outer transaction
    early - there'd be nothing left to roll back, and test data would
    leak into the test database permanently.

    The fix is a nested SAVEPOINT: we open a real transaction, then a
    SAVEPOINT inside it, and bind the session to that. When app code
    calls `session.commit()`, SQLAlchemy only releases the SAVEPOINT -
    the outer transaction is untouched. The event listener below opens a
    fresh SAVEPOINT immediately after each one ends, so this keeps
    working even if the code commits multiple times in one test (this
    workflow commits at least three times: ticket persistence, workflow
    run creation, and each status update). At teardown we roll back the
    outer transaction, which discards every SAVEPOINT and every write
    with it - regardless of how many inner commits happened.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = session_factory()

    nested_savepoint = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(session, transaction_):
        nonlocal nested_savepoint
        if not nested_savepoint.is_active:
            nested_savepoint = connection.begin_nested()

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


@pytest.fixture()
def mock_jira_and_slack(monkeypatch):
    """
    Replace the real Jira and Slack HTTP calls with no-op fakes that just
    record what they were called with.

    Why: jira_service and slack_notification_service are module-level
    singletons (`jira_service = JiraService()`), so there's only ever one
    instance in the whole app - patching a method directly on that
    instance affects every module that imported it, including
    workflow_service. Without this, tests would try to make real HTTP
    calls using the fake test credentials from the top of this file and
    fail with a connection or auth error instead of testing our own logic.
    """
    from types import SimpleNamespace

    from app.services.jira_service import jira_service
    from app.services.slack_notification_service import slack_notification_service

    jira_calls = []
    slack_messages = []

    def fake_update_issue_priority(issue_key, priority):
        jira_calls.append({"issue_key": issue_key, "priority": priority})

    def fake_send_message(message):
        slack_messages.append(message)

    monkeypatch.setattr(jira_service, "update_issue_priority", fake_update_issue_priority)
    monkeypatch.setattr(slack_notification_service, "send_message", fake_send_message)

    return SimpleNamespace(jira_calls=jira_calls, slack_messages=slack_messages)
