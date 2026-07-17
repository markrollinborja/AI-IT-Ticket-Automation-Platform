# API Design

## Overview

The AI IT Ticket Automation Platform exposes a small set of REST endpoints focused on workflow automation, Jira integration, and operational visibility.

The API is intentionally lightweight because Jira is the system of record. The platform primarily reacts to Jira webhook events rather than providing full ticket management.

---

# API Principles

The API is designed around the following principles:

- Jira-first architecture
- RESTful endpoint design
- Stateless request handling
- Separation of concerns
- Service-oriented architecture
- Clear responsibility for each endpoint

---

# API Endpoints

## Health

### GET /health

Returns the application health status.

**Purpose**

- Health checks
- Docker verification
- Deployment monitoring

---

## Jira Webhooks

### POST /webhooks/jira

Receives webhook events from Jira Cloud.

**Responsibilities**

- Validate incoming webhook payload
- Persist ticket data
- Start workflow execution
- Execute Rule Engine
- Call OpenAI if required
- Update Jira priority
- Record workflow history
- Send Slack notification

---

## Tickets

### GET /tickets

Returns persisted tickets.

---

### POST /tickets

Creates a ticket manually for local development and testing.

This endpoint exists primarily for development purposes. In production, Jira is expected to create tickets.

---

## Workflow Runs

### GET /workflow-runs

Returns all workflow executions.

Information includes:

- Workflow status
- Final priority
- Classification source
- Started time
- Completed time

---

### GET /workflow-runs/{workflow_run_id}

Returns detailed information for a single workflow execution.

Includes:

- Workflow metadata
- AI metadata
- Timeline
- Audit logs
- Error information (if applicable)

---

## Dashboard

### GET /dashboard

Returns the workflow dashboard.

Displays:

- Total workflows
- Completed workflows
- Pending workflows
- Failed workflows
- Workflow execution history

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
 └── OpenAI
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

The API follows a fail-safe workflow.

If an unexpected error occurs:

- WorkflowRun is marked as Failed.
- Failure details are persisted.
- AuditLog records the failure.
- Slack receives a failure notification.
- The exception is logged for troubleshooting.

---

# Version 1 Scope

Version 1 intentionally limits AI functionality to priority classification only.

Future API enhancements may include:

- Category prediction
- Support team recommendation
- Suggested responses
- Approval workflow endpoints
