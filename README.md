# AI IT Ticket Automation Platform

An enterprise-style IT ticket automation platform that automates IT ticket prioritization using a hybrid workflow of deterministic business rules and AI-powered classification.

Instead of sending every ticket to AI, the platform follows a rule-engine-first architecture. Known ticket patterns are handled instantly using deterministic rules, while only unmatched tickets are classified using OpenAI. This approach reduces AI cost, improves response time, and reflects how enterprise automation platforms are commonly designed.

The platform integrates with Jira Cloud through webhooks, updates ticket priorities automatically, records a complete workflow audit trail, sends Slack notifications, and provides a dashboard for monitoring workflow executions.

This project demonstrates enterprise workflow automation using modern backend engineering practices, third-party integrations, and AI-assisted decision making.

---

## Tech Stack

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic

### Artificial Intelligence

- OpenAI API
- GPT-4o-mini

### Integrations

- Jira Cloud REST API
- Jira Webhooks
- Slack Incoming Webhooks

### Infrastructure

- Docker
- Docker Compose
- ngrok (Local Webhook Testing)

### Frontend

- Jinja2
- Bootstrap 5

---

## Key Features

### Workflow

- Jira-first workflow architecture
- Workflow execution tracking
- Audit logging for every workflow event

### Classification

- Rule Engine priority classification
- OpenAI fallback priority classification
- AI confidence score persistence

### Integrations

- Automatic Jira priority updates
- Slack workflow notifications

### Monitoring

- Dashboard for monitoring workflow runs
- Workflow details page with execution timeline

### Infrastructure

- Dockerized local development environment

---

## Project Status

**Version:** 1.0 MVP

### Completed

- Jira Cloud webhook integration
- Rule Engine priority classification
- OpenAI fallback priority classification
- Workflow tracking
- Audit logging
- Slack notifications
- Dashboard
- Dockerized local development

### Planned for Version 2

- Category classification
- Support team recommendation
- Suggested responses
- Approval workflows

---

## System Architecture

The platform follows a **Jira-first, Rule Engine-first** architecture designed to mirror enterprise IT automation workflows.

```text
User
│
▼
Jira Ticket Created
│
▼
Jira Webhook
│
▼
FastAPI
│
▼
Workflow Service
│
▼
Persist Ticket
│
▼
Create WorkflowRun
│
▼
Approval Policy Check
│
▼
Rule Engine
│
├────────────── Rule Matched ──────────────┐
│                                          │
│                                          ▼
│                               Update Jira Priority
│                                          │
│                                          ▼
│                                Record Audit Logs
│                                          │
│                                          ▼
│                             Send Slack Notification
│                                          │
│                                          ▼
│                               Workflow Completed
│
└────────────── No Rule Match ─────────────┐
                                           │
                                           ▼
                                OpenAI Classification
                                           │
                                           ▼
                         Save AI Priority & Confidence
                                           │
                                           ▼
                               Update Jira Priority
                                           │
                                           ▼
                                Record Audit Logs
                                           │
                                           ▼
                             Send Slack Notification
                                           │
                                           ▼
                               Workflow Completed
```

### Workflow Summary

1. Jira receives a new IT support ticket.
2. Jira sends a webhook to the FastAPI application.
3. The ticket is persisted in PostgreSQL.
4. A WorkflowRun is created to track execution.
5. The approval policy is evaluated.
6. The Rule Engine attempts to classify the ticket priority.
7. If no rule matches, OpenAI classifies the priority.
8. The final priority is written back to Jira.
9. Audit logs are recorded throughout the workflow.
10. Slack is notified and the workflow is marked complete.

---

## Architecture & Design Decisions

### Jira-first architecture

Jira is the source of truth for tickets. The application does not create Jira tickets. Instead, it reacts to Jira webhooks, processes the ticket, and writes the result back to Jira.

This mirrors how internal enterprise automation systems usually work: automation layers enhance existing business platforms instead of replacing them.

### Rule Engine first, AI fallback second

The Rule Engine always runs before OpenAI.

Known ticket patterns are handled deterministically because rules are:

- faster
- cheaper
- easier to test
- easier to audit
- more predictable

OpenAI is only used when no rule matches. This keeps AI usage focused, controlled, and cost-efficient.

### AI only classifies priority in Version 1

Version 1 intentionally limits AI to priority classification only.

The AI returns:

```json
{
  "priority": "high",
  "confidence_score": 0.95
}
```

The confidence score is saved for audit visibility, but it does not control workflow behavior.

### WorkflowRun tracking

Every Jira webhook execution creates a WorkflowRun record.

This makes it possible to track:

- workflow status
- final priority
- classification source
- AI metadata
- start time
- completion time
- failure information

### Audit logging

Important workflow events are stored as audit logs.

This creates a traceable history of what happened during each automation run, including classification, Jira updates, workflow completion, and failures.