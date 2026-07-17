# Security Review

## Overview

This document summarizes the security posture of the AI IT Ticket Automation Platform as
actually implemented, and what's intentionally deferred.

The objective is practical security controls appropriate for a portfolio project at this
scale — not maximal security theater. Every control listed below either exists in the code
today or is explicitly marked as planned.

---

# Implemented

## Secret Management

Secrets are never committed to source control.

- All credentials (`JIRA_API_TOKEN`, `SLACK_WEBHOOK_URL`, `OPENAI_API_KEY`,
  `DATABASE_URL`, etc.) are loaded from environment variables via `api/app/core/config.py`
  (Pydantic `Settings`), sourced from `api/.env`, which is gitignored.
- `api/.env.example` documents every required variable without real values.
- gitleaks runs as a pre-commit hook (`.pre-commit-config.yaml`) and scans every commit for
  accidentally-included secrets before they can even be committed locally.

## Dependency Security

- `pip-audit` runs in CI (`.github/workflows/ci.yml`, `security` job) against both
  `requirements.txt` and `requirements-dev.txt` on every push and pull request, flagging
  known-vulnerable dependency versions.
- Dependabot (`.github/dependabot.yml`) opens weekly, grouped pull requests to keep
  dependencies patched — Python packages, GitHub Actions, and pre-commit hook revisions.

## Configuration Validation

- `ENVIRONMENT` and `LOG_LEVEL` are `Literal`-typed in `Settings`. An invalid value fails
  app startup immediately with a clear Pydantic validation error, instead of silently
  running with a misconfigured or unexpected value.

## Database Protection

- All database access goes through SQLAlchemy's ORM with parameterized queries. No raw SQL
  string interpolation is used, which prevents SQL injection.

## Error Responses

- The global exception handler (`api/app/core/error_handlers.py`) returns a generic
  `{"detail": "Internal server error..."}` response for unhandled exceptions. Stack traces,
  SQL, and internal details are never returned to the client — they go to the application
  log instead (`logger.exception(...)`), which only the operator sees.

## Container Security

- The Docker image (`api/Dockerfile`) runs as a non-root user (`appuser`), not root.
- The multi-stage build means build tooling doesn't end up in the runtime image.

## Input Validation

- FastAPI + Pydantic schemas validate request bodies (types, required fields) before a
  request reaches business logic.
- `app/services/jira_webhook_validation_service.py` validates that incoming webhook
  payloads have the expected structure and a supported event type before a workflow starts.
  This rejects malformed requests, but it is **not** authentication — see the next section.

---

# Not Implemented (Intentionally Deferred)

- **No authentication anywhere.** The dashboard, API routes, and webhook endpoint are all
  open. See [09-authentication-strategy.md](09-authentication-strategy.md) for the planned
  approach and why it hasn't been built yet.
- **No Jira webhook signature/secret validation.** `/webhooks/jira` checks payload shape,
  not origin. Anyone who knows the URL can POST a well-formed payload to it today.
- **No SSO, OAuth, SAML, or MFA.** Not relevant at this project's scale.
- **No rate limiting or WAF.** Would matter more once the app is deployed publicly and
  left running.
- **No SIEM / centralized log aggregation.** Logs are plain text to stdout; see
  [11-logging-strategy.md](11-logging-strategy.md).
- **Email is not an integration in this project.** There is no SMTP credential to secure
  because there is no email-sending code.

These gaps matter more once the app is deployed and reachable publicly. Per
[project-roadmap.md](project-roadmap.md), public deployment is the next planned step —
at minimum, basic auth and webhook validation should be revisited around that time if real
third-party credentials (Jira, Slack, OpenAI) will be wired up against a publicly
reachable instance.

---

# Security Design Principles

- Secure by default where it costs little (env-based secrets, non-root containers,
  parameterized queries, generic error responses)
- Automate what can be automated (gitleaks, pip-audit, Dependabot) rather than relying on
  manual review to catch secrets or vulnerable dependencies
- Be honest in documentation about what's built versus deferred, rather than describing
  aspirational controls that don't exist in the code
