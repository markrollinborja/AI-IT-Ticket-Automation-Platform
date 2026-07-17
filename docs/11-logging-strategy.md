# Logging Strategy

## Overview

The platform logs to stdout so operators and engineers can troubleshoot workflow failures
and integration issues, both locally and via `docker compose logs` / a hosting platform's
log viewer.

---

## Log Format

Logs are plain text, not structured JSON. Configured in
`api/app/core/logging.py`:

```text
%(asctime)s | %(levelname)s | %(name)s | %(message)s
```

Example:

```text
2026-07-17 10:15:30,123 | INFO | app.request | POST /webhooks/jira -> 200 (842.3ms)
2026-07-17 10:15:31,004 | ERROR | app.services.workflow_service | Workflow failed for Jira issue OPS-123
```

Plain text was chosen over structured JSON because this project doesn't (yet) ship logs to
an aggregator like Datadog or an ELK stack that would benefit from structured fields —
stdout text that's readable directly in the terminal or `docker compose logs` is simpler
and sufficient at this scale. If log aggregation becomes relevant (e.g. after public
deployment with real traffic), switching to structured JSON logging is a contained change
localized to `logging.py` — see [project-roadmap.md](project-roadmap.md), Future Ideas.

---

## Log Level

Configurable via the `LOG_LEVEL` environment variable (`DEBUG`, `INFO`, `WARNING`, or
`ERROR`), validated at startup as a `Literal` type in `Settings` — an invalid value fails
fast instead of silently defaulting.

---

## What Gets Logged

### Request logging (all routes)

`api/app/core/middleware.py` logs every HTTP request: method, path, response status code,
and duration in milliseconds, via the `app.request` logger.

### Workflow events

`app/services/workflow_service.py` logs key points in the webhook-triggered workflow:
workflow start, completion, and failure (with full traceback via `logger.exception(...)`
on failure).

### Unhandled exceptions

`api/app/core/error_handlers.py`'s global exception handler logs the full exception via
`logger.exception(...)` before returning a generic error response to the client — the
traceback goes to the log, never to the API response.

---

## What's Deliberately Not Logged

Sensitive values are never logged: `JIRA_API_TOKEN`, `OPENAI_API_KEY`,
`SLACK_WEBHOOK_URL`, and `DATABASE_URL` are only read from `Settings` for making outbound
calls, never passed to a logging call.

---

## Correlating Logs to a Workflow

There's no request-ID or correlation-ID field threaded through log lines yet. To trace a
specific workflow's history today, use the `WorkflowRun` and `AuditLog` database records
(via `GET /workflow-runs/{id}`) rather than grepping logs — the audit trail is the source
of truth for "what happened to this ticket," and logs are for operational/debugging
visibility around it.

---

## Design Decision

Keep logging simple and readable for a single-service, single-environment-at-a-time
project. Structured logging, correlation IDs, and log aggregation are reasonable additions
if this project ever runs at a scale where grepping stdout stops being practical, but
adding them now would be solving a problem this project doesn't have yet.
