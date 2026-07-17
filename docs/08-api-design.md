# API Design

## Overview

The AI IT Ticket Automation Platform exposes a small set of REST endpoints focused on
workflow automation, Jira integration, and operational visibility, plus a server-rendered
dashboard.

The API is intentionally lightweight because Jira is the system of record. The platform
primarily reacts to Jira webhook events rather than providing full ticket management.

---

# API Principles

- Jira-first architecture
- RESTful endpoint design
- Stateless request handling
- Separation of concerns (routes stay thin; business logic lives in `app/services/`)

---

# API Endpoints

This list matches `api/app/api/routes/` exactly.

## Health

### GET /health

Liveness check. Zero dependencies — returns immediately regardless of database state.

### GET /health/ready

Readiness check. Actually queries the database (`SELECT 1`); returns `503` with
`{"status": "not_ready", "reason": "database_unavailable"}` if the database is
unreachable, or `{"status": "ready"}` otherwise. See
[14-deployment-plan.md](14-deployment-plan.md) for why these are separate endpoints.

---

## Jira Webhooks

### POST /webhooks/jira

Receives webhook events from Jira Cloud. This is the entry point for the entire automation
workflow:

- Validate incoming webhook payload structure and event type
- Persist ticket data
- Create a `WorkflowRun`
- Execute the Rule Engine, falling back to OpenAI if no rule matches
- Update the ticket priority back in Jira
- Record `AuditLog` events throughout
- Send a Slack notification on completion or failure

---

## Tickets

### POST /tickets

Creates a ticket manually. Exists for local development and testing — in production, Jira
is the only real source of tickets, via the webhook above. There is currently no `GET
/tickets` endpoint; tickets are viewed through workflow runs instead (see below).

---

## Workflow Runs

### GET /workflow-runs

Returns all workflow executions: status, final priority, classification source, start/
completion time.

### GET /workflow-runs/{workflow_run_id}

Returns a single workflow execution's full detail.

### GET /workflow-runs/{workflow_run_id}/audit-logs

Returns the audit log entries for a single workflow execution, in chronological order.

---

## Dashboard

### GET /dashboard

Server-rendered (Jinja2) operations dashboard. Shows the 25 most recent workflow runs with
their ticket, status, priority, and classification source.

### GET /dashboard/workflow-runs/{workflow_run_id}

Server-rendered detail page for a single workflow run: full metadata plus its audit log
timeline. Returns `404` if the workflow run doesn't exist.

---

# Request Flow

```text
Jira
 │
 ▼
POST /webhooks/jira
 │
 ▼
Workflow Service
 │
 ▼
Rule Engine
 │
 ├── Rule Matched
 │
 └── OpenAI (fallback)
 │
 ▼
Update Jira
 │
 ▼
Audit Log
 │
 ▼
Slack
```

---

# Error Handling

See [10-error-handling-strategy.md](10-error-handling-strategy.md) for the full strategy.
In short: workflow failures mark the `WorkflowRun` as `failed`, record an `AuditLog` entry,
send a Slack failure notification, and return a generic `500` to the caller — full detail
is in the database, not the HTTP response.

---

# Not Yet Implemented

- No authentication on any route — see [09-authentication-strategy.md](09-authentication-strategy.md)
- No `GET /tickets` (list) or filtering/search on `GET /workflow-runs`
- No category prediction, support team recommendation, or suggested-response endpoints —
  AI is scoped to priority classification only (see
  [16-ai-classification-strategy.md](16-ai-classification-strategy.md))
- No approval decision endpoints — `approval_required` is a boolean gate evaluated during
  the workflow, not a separate approve/reject action
