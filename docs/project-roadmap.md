# Project Roadmap

## Overview

The AI IT Ticket Automation Platform is a portfolio project that demonstrates enterprise
backend engineering, workflow automation, third-party API integrations, AI-assisted
decision making, and the professional engineering practices a real team uses to ship and
maintain software.

The roadmap is split into versions with different goals:

- **Version 1** built the business functionality: Jira integration, the Rule Engine + AI
  hybrid classification workflow, Slack notifications, and the dashboard.
- **Version 2** turned the working V1 prototype into something that looks and behaves like
  a real team's codebase: tested, linted, scanned for security issues, documented, and
  deployable with a single command. It also picked up one piece of real new functionality
  along the way - the approval workflow - which is called out separately below since it
  doesn't fit "engineering practices, not features."
- **Version 3** is public deployment: taking this from "runs on localhost" to "a live URL a
  hiring manager can actually click." Not started yet - see below.

Version 1 and Version 2 are feature-complete as of this writing.

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

## Approval Workflow (Business Feature)

This one's a genuine exception to "Version 2 is engineering practices, not new business
features" - it's real new functionality, added after Version 2 was underway. Worth calling
out separately rather than blending it into the engineering-practices list above.

- `approvals` table and `Approval` model tracking the human decision (`pending`/`approved`/
  `rejected`), independent of `workflow_runs`
- Approval Policy Service rewritten to evaluate ticket category (security-sensitive change,
  financial/payroll access, software purchase) instead of reporter identity. Outages and
  executive-impact requests were tried as gated categories and deliberately removed -
  approval only makes sense for risk that can wait, and urgency should never be gated. See
  [project-decisions.md](project-decisions.md), Decision #9
- A real pause, not just a database flag: Jira's priority is set to a **Pending**
  workflow-state value immediately, and the workflow genuinely stops - the real classified
  priority is not pushed to Jira and the workflow does not complete until a decision is made
- `POST /workflow-runs/{id}/approve` and `/reject` resume or terminate the paused workflow;
  rejecting pushes a **Rejected** workflow-state value to Jira
- Dashboard gained a Pending Approvals section with Approve/Reject actions (a small modal +
  `fetch()` call, not a separate frontend - consistent with Decision #8)
- See [project-decisions.md](project-decisions.md), Decision #9, for the full reasoning,
  and [05-user-flow.md](05-user-flow.md), Step 7, for the user-facing behavior

---

# In Progress

Nothing is actively in progress. Version 1 and Version 2 are feature-complete.

---

# Version 3 (Next)

## Goal

Public deployment: take this from "runs on `localhost`" to a live URL, so a hiring manager
can click through the real thing instead of reading code. Everything needed to deploy
responsibly is already in place from Version 2 - CI, health/readiness checks,
containerization, environment-based config - so this is entirely about hosting and access
control, not more application engineering.

## Planned Scope

- **Hosting: Render (app) + Neon (Postgres).** Both have genuinely permanent free tiers
  (not trials) - Render's own bundled Postgres was considered and rejected because its free
  tier expires 30 days after creation and gets deleted after a 14-day grace period, which
  doesn't work for a project meant to sit on a resume indefinitely. The tradeoff is a
  30-60 second cold start on the first request after either service has been idle
  (Render: 15 min, Neon: 5 min) - acceptable for a portfolio demo, not acceptable for a
  real production SLA.
- **Basic access protection.** Zero authentication exists today (see
  [09-authentication-strategy.md](09-authentication-strategy.md)), which is fine on
  `localhost` but not once real Jira/Slack/OpenAI credentials are reachable from the public
  internet. A shared bearer token protecting the dashboard/API, plus some form of webhook
  origin check, should ship alongside the deployment itself rather than after it.
- Verify the full webhook → Rule Engine/AI → Jira → Slack → dashboard → approval flow
  works end-to-end against the live deployment, the same way it was verified locally.

---

# Future Ideas

Not started, and only worth doing if they clearly increase hiring value relative to their
complexity:

## AI

- Category classification
- Support team recommendation
- Suggested first-response generation

## Workflow

- Workflow retry policies for failed steps
- Configurable business rules (move `rule_engine.py`'s hardcoded conditions into a database
  table so they can change without a redeploy) - discussed alongside the approval workflow,
  deferred for now

## Platform

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
  by tests, the TestClient `raise_server_exceptions` quirk) and the approval workflow
  (resumable workflow state, Jira-as-status-indicator, the deliberate choice not to build
  department-based approver routing)
- Demo script
