"""
API test for the /health endpoint.

This is the simplest possible endpoint - it doesn't touch the database
or any external service - which is exactly why it's the first test to
write against the `client` fixture. If this test passes, it proves the
whole test harness works end-to-end: test database created, tables
built, dependency override wired, TestClient able to boot the app.
Every later API test builds on this same foundation.
"""


def test_health_check_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "AI IT Ticket Automation Platform API"
    assert "version" in body
    assert "environment" in body


def test_readiness_check_returns_ready_when_db_is_reachable(client):
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_check_returns_503_when_db_is_unreachable(client, db_session, monkeypatch):
    """
    Simulates the database being unreachable by making the injected
    session's own execute() raise, instead of actually taking Postgres
    down - same idea as mock_jira_and_slack: fake the failure at the
    boundary the endpoint talks to, not the real infrastructure.
    """
    from sqlalchemy.exc import SQLAlchemyError

    def failing_execute(*args, **kwargs):
        raise SQLAlchemyError("simulated database failure")

    monkeypatch.setattr(db_session, "execute", failing_execute)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready", "reason": "database_unavailable"}
