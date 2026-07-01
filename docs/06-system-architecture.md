# System Architecture

## Overview

The AI IT Ticket Automation Platform uses a modular monolith architecture.

The system is designed as a single deployable backend application with clearly separated internal modules for Jira integration, workflow orchestration, AI analysis, business rules, approvals, notifications, audit logging, and dashboard APIs.

This approach provides a production-quality architecture while avoiding unnecessary distributed system complexity for Version 1.

---

## Architecture Style

**Architecture Pattern:** Modular Monolith

The platform is deployed as one backend service, but the codebase is organized into independent modules with clear responsibilities.

This allows the system to remain simple to deploy while still supporting maintainability, testability, and future expansion.

---

## High-Level Architecture

```text
Employee
   ↓
Jira
   ↓
Jira Webhook
   ↓
FastAPI Backend
   ↓
PostgreSQL Audit Database
   ↓
React Admin Dashboard
```

---

## Core Components

### React Admin Dashboard

Provides administrators with visibility into ticket status, workflow execution, approval state, notification history, and system metrics.

### FastAPI Backend

Acts as the main application layer for receiving webhook events, executing workflows, exposing dashboard APIs, and coordinating internal modules.

### PostgreSQL Database

Stores ticket metadata, AI recommendations, business rule decisions, approval records, notification events, workflow execution history, and audit logs.

### Jira Integration Module

Receives Jira webhook events and retrieves ticket details when needed.

### Webhook Module

Validates incoming Jira webhook requests before workflow execution begins.

### Workflow Orchestration Module

Coordinates the end-to-end automation process for each ticket.

### AI Analysis Module

Uses the OpenAI API to classify tickets, recommend priority, recommend support team, identify missing information, and generate first response suggestions.

### Business Rules Module

Applies deterministic workflow rules after AI analysis to enforce NorthStar Retail policies.

### Approval Module

Creates and tracks approval requests when a workflow requires human review.

### Notification Module

Sends Slack and email notifications based on workflow events and business rule outcomes.

### Audit Logging Module

Records every workflow step, decision, error, and integration event for traceability.

### Dashboard API Module

Exposes backend endpoints used by the React Admin Dashboard.

---

## Request Flow

```text
1. Employee creates a ticket in Jira.
2. Jira sends a webhook event to the FastAPI backend.
3. The Webhook Module validates the request.
4. The Jira Integration Module retrieves or normalizes ticket data.
5. The Workflow Orchestration Module starts the ticket workflow.
6. The AI Analysis Module analyzes the ticket.
7. The Business Rules Module evaluates workflow decisions.
8. The Approval Module creates an approval request if needed.
9. The Notification Module sends Slack and email notifications.
10. The Audit Logging Module records workflow events.
11. The Dashboard API Module exposes workflow status to the React Admin Dashboard.
```

---

## Internal Module Design

```text
FastAPI Backend
│
├── Webhook Module
├── Jira Integration Module
├── Workflow Orchestration Module
├── AI Analysis Module
├── Business Rules Module
├── Approval Module
├── Notification Module
├── Audit Logging Module
└── Dashboard API Module
```

---

## External Integrations

| Integration | Purpose |
|------------|---------|
| Jira | Source of IT support tickets |
| OpenAI API | AI-assisted ticket analysis |
| Slack API | Team notifications |
| Email Service | Stakeholder notifications |
| PostgreSQL | Audit and workflow data storage |

---

## Architecture Principles

The system follows these principles:

- Keep Version 1 simple and deployable.
- Use a modular monolith instead of premature microservices.
- Separate AI recommendations from deterministic business rules.
- Treat Jira as the ticket system of record.
- Maintain complete audit history.
- Keep humans in control of sensitive workflow decisions.
- Design modules so future integrations can be added with minimal disruption.

---

## Version 1 Architecture Decision

Version 1 will not use a microservice architecture.

The platform does not require independently deployed services at this stage. A modular monolith provides enough separation of concerns while reducing operational overhead, deployment complexity, and development time.

If the system grows in future versions, modules such as AI Analysis, Notification, or Workflow Orchestration could be extracted into separate services.