# Project Roadmap

## Overview

The AI IT Ticket Automation Platform is a portfolio project that demonstrates enterprise
backend engineering, workflow automation, third-party API integrations, AI-assisted
decision making, and the professional engineering practices a real team uses to ship and
maintain software.

The roadmap is split into two versions with different goals:

- **Version 1** built the business functionality: Jira integration, the Rule Engine + AI
  hybrid classification workflow, Slack notifications, and the dashboard.
- **Version 2** did not add new business features. It turned the working V1 prototype into
  something that looks and behaves like a real team's codebase: tested, linted, scanned for
  security issues, documented, and deployable with a single command.

Both are feature-complete as of this writing.

---

# Completed

## Version 1 — Core Platform

- FastAPI backend, PostgreSQL, SQLAlchemy ORM (tables created via `Base.metadata.create_all()` — no migration tool is in use yet)
- Jira Cloud webhook integration (Jira-first: the app never creates Jira tickets, only reacts to them)
- Rule Engine — deterministic priority classification
- OpenAI (GPT-4o-mini) fallback classification, used only when no rule matches
- WorkflowRun tracking and AuditLog history for full traceability
- Automatic Jira priority updates
- Slack workflow notifications
- Server-rendered operations dashboard (Jinja2 + Bootstrap)
- Docker Compose for local development

## Version 2 — Engineering Practices

### Automated testing

- pytest suite covering the Rule Engine, health/readiness endpoints, and the full Jira
  webhook workflow (success path, approval-required path, unsupported event type, and a
  Jira-failure path that verifies the app fails safely)
- Real PostgreSQL test database, self-provisioning, with SAVEPOINT-based transactional
  isolation between tests
- See [15-testing-strategy.md](15-testing-strategy.md)

### CI/CD

- GitHub Actions (`.github/workflows/ci.yml`): `lint`, `test`, and `security` jobs run in
  parallel on every push and pull request
- `test` job runs against a real ephemeral Postgres service container, not SQLite
- Dependabot (`.github/dependabot.yml`): weekly, grouped dependency update PRs for pip,
  GitHub Actions, and pre-commit hooks

### Code quality tooling

- Ruff for linting and formatting (replaces the originally-planned Black + isort — one
  tool, same result, faster)
- Configuration lives in `pyproject.toml`

### Pre-commit hooks

- `.pre-commit-config.yaml`: Ruff (lint + format), file hygiene checks (trailing
  whitespace, merge conflict markers, large files), and gitleaks secret scanning — all run
  locally before a commit is even made

### Security and dependency scanning

- `pip-audit` runs in CI against both `requirements.txt` and `requirements-dev.txt`
- gitleaks scans every commit for accidentally-committed secrets
- Dependabot keeps dependencies patched automatically
- See [12-security-review.md](12-security-review.md)

### Logging and error handling

- Configurable log level via `LOG_LEVEL` env var (`DEBUG`/`INFO`/`WARNING`/`ERROR`)
- Global FastAPI exception handler returns a safe, generic error response instead of
  leaking stack traces
- Request logging middleware logs method, path, status code, and duration for every request

### Configuration and environment

- `ENVIRONMENT` and `LOG_LEVEL` are `Literal`-typed in `Settings` (Pydantic) — invalid
  values fail fast at startup instead of silently misconfiguring the app

### Health and readiness endpoints

- `GET /health` — liveness, zero dependencies
- `GET /health/ready` — readiness, actually queries the database, returns 503 if unreachable

### Docker improvements

- Multi-stage `Dockerfile`: dependencies built in a separate stage, only the resulting
  virtual environment and app code copied into the runtime image
- Runs as a non-root user
- `HEALTHCHECK` against `/health`
- `docker-compose.yml`: `db` has a `pg_isready` healthcheck; `api` waits for `db` to report
  healthy before starting (`condition: service_healthy`)

### Documentation

- README rewritten with a real "Getting Started" section, testing instructions, and
  development setup instructions
- `docs/13-folder-structure.md` and `docs/14-deployment-plan.md` rewritten to describe the
  system as actually built (previously described a never-built React frontend)
- `docs/07-database-design.md`, `docs/09-authentication-strategy.md`,
  `docs/10-error-handling-strategy.md`, `docs/11-logging-strategy.md`, and
  `docs/12-security-review.md` corrected to match the real implementation
- `docs/project-decisions.md` gained Decision #8 documenting the frontend scope-down

---

# In Progress

Nothing is actively in progress. Both Version 1 and Version 2 are feature-complete.

---

# Next Highest ROI Feature

## Public deployment

Deploy the platform to a public host (e.g. Render, Railway, or Fly.io) with a managed
Postgres instance, and verify the full webhook → Rule Engine/AI → Jira → Slack → dashboard
flow works end-to-end against the live deployment.

This is the highest-ROI next step because everything needed to deploy responsibly is
already in place — CI, health/readiness checks, containerization, and environment-based
config — and a live URL turns this from "code a hiring manager can read" into "a system
a hiring manager can actually click through," which is a meaningfully stronger portfolio
signal for Automation/Backend/Internal Tools Engineer roles.

---

# Future Ideas

Not started, and only worth doing if they clearly increase hiring value relative to their
complexity:

## AI

- Category classification
- Support team recommendation
- Suggested first-response generation

## Workflow

- Human approval decision tracking (currently a boolean gate only, no approve/reject
  workflow or approver identity)
- Workflow retry policies for failed steps

## Platform

- Authentication (bearer token or similar) for dashboard/admin endpoints
- Email notifications alongside Slack
- Structured (JSON) logging, if log aggregation ever becomes relevant
- A schema migration tool (e.g. Alembic) if the schema starts changing often enough that
  `create_all()` stops being sufficient

These are intentionally deferred. Per the project's own principles, none of them should be
built just because they sound impressive — only if they solve a real problem this project
actually has.

---

# Hiring Deliverables

Once public deployment is complete:

- Resume project entry
- GitHub portfolio polish
- LinkedIn project description
- Interview talking points and STAR stories for the Version 2 engineering work (testing
  strategy, CI/CD, the transactional test isolation bug, the tzdata production bug caught
  by tests, the TestClient `raise_server_exceptions` quirk)
- Demo script
