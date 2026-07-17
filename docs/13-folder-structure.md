# Folder Structure

## Overview

The AI IT Ticket Automation Platform is a single FastAPI backend that also serves its own
operations dashboard via server-rendered Jinja2 templates - there is no separate frontend
application. This document reflects the structure as actually built. See
[project-decisions.md](project-decisions.md), Decision #8, for why this diverged from the
original planned React/backend split.

---

# Repository Structure

```text
AI-IT-Ticket-Automation-Platform/
├── .github/
│   ├── workflows/ci.yml        # Lint, security (pip-audit), and test jobs on every push/PR
│   └── dependabot.yml          # Weekly dependency update PRs, grouped by ecosystem
├── api/                        # The FastAPI application (backend + dashboard)
│   ├── app/
│   │   ├── api/routes/         # HTTP route handlers, one file per resource
│   │   ├── core/                # Config, logging, error handling, request middleware
│   │   ├── db/                  # SQLAlchemy engine/session setup
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/             # Business logic: rule engine, Jira, Slack, AI, workflow orchestration
│   │   ├── templates/            # Jinja2 templates for the dashboard
│   │   ├── static/                # Static assets served by the dashboard
│   │   └── main.py                # FastAPI app instance and startup wiring
│   ├── Dockerfile                 # Multi-stage build, non-root user, HEALTHCHECK
│   ├── requirements.txt           # Production dependencies (exact pins)
│   └── requirements-dev.txt       # + pytest, ruff, pre-commit
├── tests/                         # pytest suite, run from the repository root
├── docs/                          # Planning and architecture documentation (this file included)
├── diagrams/                      # Architecture diagram used in the README
├── screenshots/                   # Demo screenshots used in the README
├── demo/                          # Demo GIF used in the README
├── docker-compose.yml             # API + Postgres, with healthcheck-gated startup ordering
├── .pre-commit-config.yaml        # Ruff, gitleaks, and file hygiene checks on every commit
└── pyproject.toml                 # pytest and Ruff configuration
```

---

# Design Principles

- **Single backend service.** The dashboard is server-rendered, not a separate frontend
  app - see Decision #8 in `project-decisions.md`.
- **Business logic lives in `services/`, not in route handlers.** Route files stay thin
  and are easy to read; each service can be tested independently of HTTP.
- **Tests live at the repository root (`tests/`), not nested under `api/`.** `pytest` and
  CI both run from a single, predictable root regardless of what's being tested, and
  `pyproject.toml`'s `pythonpath = ["api"]` lets tests import `app.*` the same way the app
  imports itself.
- **`core/` holds cross-cutting concerns** (config, logging, error handling, middleware)
  separately from `services/` (business logic) and `api/routes/` (HTTP layer), so it's
  clear where a given piece of code belongs.

---

# Design Decision

The original plan called for a monorepo with a separate `backend/` and `frontend/` split
(a React application talking to a REST API). That was scoped down during implementation in
favor of a single FastAPI service that renders its own dashboard - see Decision #8 in
`project-decisions.md` for the reasoning. This file previously described that original,
never-built structure; it's been updated to describe what was actually shipped.
