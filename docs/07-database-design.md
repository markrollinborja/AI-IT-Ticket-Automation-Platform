# Database Design

## Overview

The AI IT Ticket Automation Platform uses PostgreSQL as the primary database for storing
ticket metadata, workflow execution history, AI recommendations, and audit logs.

The database is designed to support traceability, troubleshooting, and operational
visibility. This document describes the schema as actually implemented in
`api/app/models/`.

---

## Database Technology

**Database:** PostgreSQL

PostgreSQL was selected because it is reliable, widely adopted in enterprise environments,
supports relational data modeling, and provides strong compatibility with FastAPI-based
applications.

Tables are created via SQLAlchemy's `Base.metadata.create_all()` at application startup.
There is no migration tool (e.g. Alembic) in place yet — see
[project-roadmap.md](project-roadmap.md), Future Ideas, for when that would become worth
adding.

---

## Core Tables

## 1. tickets

Stores ticket data received from Jira.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| jira_issue_key | VARCHAR(50) | Jira issue key, unique |
| title | VARCHAR(255) | Ticket title |
| description | TEXT | Ticket description |
| reporter | VARCHAR(255) | Ticket reporter |
| source | VARCHAR(50) | Source system (defaults to `jira`) |
| created_at | TIMESTAMPTZ | Ticket creation time |
| updated_at | TIMESTAMPTZ | Last update time |

---

## 2. workflow_runs

Tracks each automation workflow run for a ticket.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| ticket_id | UUID | Foreign key → `tickets.id` |
| status | VARCHAR(50) | `processing`, `completed`, `failed` |
| ai_category | VARCHAR(100) | Reserved for future AI category classification (not populated in V1/V2 — see [16-ai-classification-strategy.md](16-ai-classification-strategy.md)) |
| ai_priority | VARCHAR(50) | AI-recommended priority, when the Rule Engine had no match |
| ai_support_team | VARCHAR(100) | Reserved for future AI support-team recommendation (not populated) |
| ai_confidence_score | FLOAT | AI confidence score |
| ai_missing_information | TEXT | Reserved for future use (not populated) |
| ai_suggested_response | TEXT | Reserved for future use (not populated) |
| final_category | VARCHAR(100) | Reserved for future use (not populated) |
| final_priority | VARCHAR(50) | Final priority after Rule Engine / AI classification |
| final_support_team | VARCHAR(100) | Reserved for future use (not populated) |
| approval_required | BOOLEAN | Whether the workflow requires human approval before proceeding |
| approval_reason | TEXT | Why approval was required |
| error_type | VARCHAR(100) | Error type, if the workflow failed |
| error_message | TEXT | Error details, if the workflow failed |
| started_at | TIMESTAMPTZ | Workflow start time |
| completed_at | TIMESTAMPTZ | Workflow completion time |
| created_at | TIMESTAMPTZ | Row creation time |
| updated_at | TIMESTAMPTZ | Last update time |

A handful of columns (`ai_category`, `ai_support_team`, `ai_missing_information`,
`ai_suggested_response`, `final_category`, `final_support_team`) exist on the model already
but are intentionally unused right now — AI is scoped to priority classification only. They
were added ahead of time so that expanding AI scope later is a service-layer change, not a
schema migration.

---

## 3. audit_logs

Stores the workflow audit trail.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| workflow_run_id | UUID | Foreign key → `workflow_runs.id` |
| event | VARCHAR(100) | Event type (e.g. `rule_matched`, `jira_updated`, `slack_notified`) |
| message | TEXT | Human-readable event description |
| created_at | TIMESTAMPTZ | Event timestamp |

---

## Entity Relationships

```text
tickets
   │
   └── workflow_runs
            │
            └── audit_logs
```

One ticket can have multiple workflow runs (e.g. if Jira resends a webhook). One workflow
run can have multiple audit log entries recorded as it progresses.

---

## Design Decisions

### Store AI Recommendations and Final Decisions Separately

`workflow_runs` stores both the AI's recommendation (`ai_priority`,
`ai_confidence_score`) and the final decision (`final_priority`) separately, even though
in V1/V2 the final priority is always either the Rule Engine's result or a direct pass-through
of the AI's result.

This keeps AI output auditable independently of the final business decision, which matters
if a future version introduces logic that can override or adjust the AI's recommendation.

### Separate Audit Logs from Workflow Runs

Audit logs are a separate table rather than a JSON column on `workflow_runs` because they
represent a sequence of events over time, not a single row's current state. This preserves
a full timeline per workflow run without overloading the `workflow_runs` row itself.

---

## Not Implemented

The following were part of earlier planning but are **not** in the current schema. They are
listed here so this document doesn't silently disagree with the code:

- **`approvals` table** — there is no separate approval request/decision entity.
  `workflow_runs.approval_required` and `approval_reason` are the entire extent of the
  approval feature: a boolean gate with a reason, evaluated at workflow time. There's no
  approve/reject action or approver identity tracked.
- **`notifications` table** — Slack messages are sent directly by
  `slack_notification_service` and are not persisted as their own record. Whether a
  notification was sent is only visible in the `audit_logs` entries for that workflow run.
- **`business_rules` table** — rules are hardcoded in `app/services/rule_engine.py`, not
  stored in the database or editable at runtime.
- User profile management, role-based permissions, multi-tenant support — no auth exists
  yet at all (see [09-authentication-strategy.md](09-authentication-strategy.md)).

Building any of these is tracked as a Future Idea in
[project-roadmap.md](project-roadmap.md), not a current gap to fix.
