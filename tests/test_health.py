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
