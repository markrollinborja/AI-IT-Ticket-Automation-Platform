# Error Handling Strategy

## Overview

The AI IT Ticket Automation Platform depends on external services — Jira, OpenAI, Slack,
and PostgreSQL. Failures in any of them are expected, and the workflow needs to fail safely
without corrupting state or losing visibility into what went wrong.

This document describes error handling as actually implemented.

---

## What Actually Happens on Workflow Failure

`workflow_service.py` wraps the entire webhook-triggered workflow (persist ticket → Rule
Engine/AI classification → update Jira → notify Slack) in a single `try`/`except`. If
anything in that chain raises:

1. The exception is logged with `logger.exception(...)` (full traceback, application logs only).
2. The `WorkflowRun` is marked `failed`, with `error_type` (the exception class name) and
   `error_message` (`str(error)`) persisted on the row.
3. An `AuditLog` entry records the failure with the same details.
4. A best-effort Slack failure notification is sent.
5. The exception is re-raised, which the global exception handler
   (`api/app/core/error_handlers.py`) turns into a generic `500` response.

This means every workflow failure — regardless of which step caused it — is fully
traceable via the `WorkflowRun` row and its `AuditLog` entries, even though the API caller
just sees a generic 500.

---

## Validation Errors

Handled separately, before a `WorkflowRun` is even created.

Examples:

- Unsupported Jira webhook event type
- Malformed webhook payload

`app/services/jira_webhook_validation_service.py` checks these up front. FastAPI/Pydantic
also reject malformed request bodies automatically via `422` responses before the route
handler runs at all.

---

## Unhandled Exceptions (Any Route)

`api/app/core/error_handlers.py` registers a catch-all handler for any exception FastAPI
doesn't already handle (i.e. anything that isn't an `HTTPException` or a Pydantic
validation error, both of which FastAPI handles on its own with proper status codes).

Response shape:

```json
{
  "detail": "Internal server error. Please try again or contact support."
}
```

This matches the shape FastAPI already uses for `HTTPException` (`{"detail": "..."}`), so
API consumers see one consistent error shape regardless of whether the error was an
explicit `HTTPException` or an unexpected crash. No stack trace, SQL, or internal detail is
ever included in the response — those go to the log via `logger.exception(...)`.

---

## Database Errors

`GET /health/ready` specifically catches `SQLAlchemyError` when checking the database
connection and returns a `503` with `{"status": "not_ready", "reason": "database_unavailable"}`
rather than letting the readiness check itself crash.

Elsewhere, database errors during a workflow are caught by the top-level workflow
`try`/`except` described above and handled the same as any other workflow failure.

---

## Not Implemented

- **Automatic retries.** A failed Jira update, OpenAI call, or Slack notification is not
  retried — the workflow is marked failed and that's the end of that run. Retrying
  external calls (with backoff) is a reasonable future improvement, tracked in
  [project-roadmap.md](project-roadmap.md), but isn't built yet.
- **Email notifications on failure.** Only Slack is notified. There is no email integration
  in this project.
- **Per-error-category response codes/bodies.** Every unhandled exception returns the same
  generic `500` body regardless of whether it was a Jira timeout, an OpenAI error, or a bug
  — the detail lives in the `WorkflowRun`/`AuditLog` rows, not in the HTTP response.

---

## Design Decision

Fail loud in the logs and the audit trail, fail generic in the API response. The operator
debugging a failure has everything they need in `WorkflowRun.error_message` and the
associated `AuditLog` entries; the API caller (Jira, or a dashboard user) only needs to
know that something went wrong, not the internal cause.
