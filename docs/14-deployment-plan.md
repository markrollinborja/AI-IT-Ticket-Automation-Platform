# Deployment Plan

## Overview

The AI IT Ticket Automation Platform is a single FastAPI service (backend + server-rendered
dashboard) backed by PostgreSQL, containerized with Docker.

Containerization provides a consistent runtime environment for development, testing, and
future production deployment. See [project-decisions.md](project-decisions.md), Decision
#8, for why this is one service rather than a separate frontend and backend.

---

# Deployment Goals

Deployment should:

- Be reproducible.
- Be simple to start.
- Support local development.
- Support future cloud deployment.
- Minimize environment-specific configuration.
- Verify itself automatically before serving traffic (see Health Checks below).

---

# Deployment Architecture

```text
FastAPI Backend (serves both the API and the dashboard)
        │
        ▼
PostgreSQL Database
```

Both services run using Docker Compose in local development. See
`docker-compose.yml` at the repository root.

---

# Containers

## Backend (`api`)

- FastAPI, serving both the JSON API and the server-rendered dashboard.
- Executes workflow automation: Jira webhook handling, Rule Engine + AI classification,
  Jira updates, Slack notifications, audit logging.
- Built from `api/Dockerfile`: a multi-stage build (dependencies installed in a builder
  stage, only the resulting virtual environment and app code copied into the runtime
  image), runs as a non-root user, and has a `HEALTHCHECK` against `/health`.

## Database (`db`)

- PostgreSQL 16.
- Stores tickets, workflow runs, and audit logs.
- Has its own `pg_isready` healthcheck in `docker-compose.yml`; the `api` container will
  not start until this reports healthy (`condition: service_healthy`), avoiding
  connection-refused errors on first startup.

---

# Environment Variables

Sensitive configuration is supplied using environment variables, loaded from `api/.env`
(never committed - see `api/.env.example` for the template). `Settings` in
`api/app/core/config.py` is the single source of truth for what's required; as of this
writing, that's:

- `APP_NAME`, `APP_VERSION` - display metadata, have safe defaults
- `ENVIRONMENT` - one of `development`, `staging`, `production`; invalid values fail at
  startup rather than silently being wrong
- `LOG_LEVEL` - one of `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `DATABASE_URL` - PostgreSQL connection string
- `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`
- `SLACK_WEBHOOK_URL`
- `OPENAI_API_KEY`, `OPENAI_MODEL`

Environment-specific configuration must never be committed to source control. Pre-commit's
gitleaks hook scans every commit for accidentally-included secrets.

---

# Docker Compose

Docker Compose orchestrates the complete local development environment.

Services:

- `api` - the FastAPI application
- `db` - PostgreSQL

A developer starts the whole platform with a single command:

```bash
docker compose up -d --build
```

See the "Getting Started" section of the root `README.md` for full setup steps.

---

# Health Checks

The backend exposes two endpoints, deliberately answering different questions:

```text
GET /health         - liveness: is the process running at all? Zero dependencies.
GET /health/ready    - readiness: can this instance serve requests right now?
                       Actually queries the database; returns 503 if unreachable.
```

Conflating these would be a mistake: a container healthcheck restarting the app because the
database had a brief hiccup doesn't fix anything and just adds downtime. `/health` drives
the Docker `HEALTHCHECK` and any future liveness probe; `/health/ready` is what a load
balancer or orchestrator should use to decide whether to route traffic to an instance.

---

# CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs three jobs in parallel on every push and
pull request to `main`:

- `lint` - Ruff lint and format checks
- `test` - the full pytest suite against a real (ephemeral) Postgres service container
- `security` - `pip-audit` against pinned dependencies

Dependabot (`.github/dependabot.yml`) opens weekly, grouped pull requests for outdated
Python packages, GitHub Actions versions, and pre-commit hook revisions.

---

# Current Scope

This project intentionally excludes:

- Kubernetes
- Load balancing / auto scaling
- Blue-green deployments
- High availability clusters
- A dedicated secrets manager (environment variables are sufficient at this scale)

These add real operational complexity that isn't justified for a project at this size and
traffic level. The goal is a deployment setup that's honest about what it needs, not one
that looks impressive by using tools it doesn't actually require.

---

# Design Decision

Docker Compose remains the deployment model because it provides a simple, portable, and
reproducible environment while keeping operational complexity proportional to the
project's actual scale. CI/CD (GitHub Actions), health/readiness checks, and dependency
scanning were added after the original Version 1 plan explicitly deferred them - they're
now in place ahead of the next step, deploying to a public host.
