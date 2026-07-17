# Testing Strategy

## Overview

The AI IT Ticket Automation Platform requires testing to ensure that workflow automation,
external integrations, business rules, and API endpoints behave reliably.

**Status: implemented.** This was originally a Version 1 plan; the described approach was
built out during Version 2 as part of the CI/testing work. See
[project-roadmap.md](project-roadmap.md).

---

## Testing Goals

- Validate core business logic.
- Confirm API endpoint behavior.
- Verify workflow execution end-to-end.
- Test business rules independently of AI.
- Support safe changes during development via CI.
- Avoid unnecessary testing complexity.

---

## What's Actually Tested (`tests/`)

### Unit tests — `test_rule_engine.py`

12 parametrized tests plus a case-insensitivity test against the Rule Engine directly, with
no database or mocking required.

### Health/readiness tests — `test_health.py`

`GET /health` returns ok; `GET /health/ready` returns ready when the database is reachable
and `503` when it isn't (simulated by monkeypatching the DB session to raise).

### Webhook/workflow integration tests — `test_webhook_jira.py`

The full `POST /webhooks/jira` flow against a real (test) PostgreSQL database, with Jira
and Slack calls faked via `monkeypatch`:

- Successful classification via the Rule Engine, workflow completes
- Approval required for an executive reporter
- Unsupported event type is rejected
- Jira update failure is handled safely and returns a clean `500` (not an unhandled crash)

### Test database

A real PostgreSQL database, not SQLite or mocks — self-provisioning (auto-creates itself if
missing) with SAVEPOINT-based transactional isolation so each test starts clean even though
the app code under test calls `session.commit()` internally. See `tests/conftest.py`.

---

## Testing Tools

- pytest + pytest-cov
- FastAPI `TestClient` (Starlette) for API tests
- Real PostgreSQL (via Docker in CI, via a local/Docker Postgres instance for local runs)
- `monkeypatch` for faking the Jira/Slack service singletons — no HTTP calls actually leave
  the test process

---

## CI Integration

Every push and pull request runs the full suite against an ephemeral Postgres service
container in GitHub Actions (`.github/workflows/ci.yml`, `test` job), with coverage
reported via `pytest --cov=app --cov-report=term-missing`.

---

## Testing Scope

Included:

- Backend unit tests (Rule Engine)
- Backend integration tests (webhook → workflow → Jira/Slack, against a real test DB)
- Health/readiness endpoint tests

Excluded (not needed at this project's scale):

- Load/performance testing
- Browser/UI automation testing (the dashboard is server-rendered and low-interactivity)
- Chaos testing
- Security penetration testing (covered instead by `pip-audit` + gitleaks, see
  [12-security-review.md](12-security-review.md))

---

## Design Decision

Test against a real PostgreSQL database rather than mocking the ORM or using SQLite. This
project is explicitly meant to demonstrate production-realistic engineering practices, and
SQLite's behavior diverges from Postgres in ways (types, constraints, transaction
semantics) that would make tests pass against a database the app doesn't actually run on in
production. The one-time cost is a self-provisioning test database fixture; the payoff is
tests that would actually catch a real Postgres-specific bug.
