# Database Design

## Overview

The AI IT Ticket Automation Platform uses PostgreSQL as the primary database for storing ticket metadata, workflow execution history, AI recommendations, business rule decisions, approvals, notifications, and audit logs.

The database is designed to support traceability, reporting, troubleshooting, and operational visibility.

---

## Database Technology

**Database:** PostgreSQL

PostgreSQL was selected because it is reliable, widely adopted in enterprise environments, supports relational data modeling, and provides strong compatibility with FastAPI-based applications.

---

## Core Tables

## 1. tickets

Stores ticket data received from Jira.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| jira_ticket_id | VARCHAR | Jira issue key |
| title | TEXT | Ticket title |
| description | TEXT | Ticket description |
| reporter_email | VARCHAR | Ticket reporter |
| status | VARCHAR | Current ticket status |
| source_platform | VARCHAR | Source system, such as Jira |
| created_at | TIMESTAMP | Ticket creation time |
| updated_at | TIMESTAMP | Last update time |

---

## 2. workflow_executions

Tracks each automation workflow run.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| ticket_id | UUID | Related ticket |
| workflow_status | VARCHAR | Pending, processing, completed, failed |
| ai_category | VARCHAR | AI-recommended category |
| ai_priority | VARCHAR | AI-recommended priority |
| ai_support_team | VARCHAR | AI-recommended support team |
| ai_confidence_score | NUMERIC | AI confidence score |
| final_category | VARCHAR | Final category after business rules |
| final_priority | VARCHAR | Final priority after business rules |
| final_support_team | VARCHAR | Final support team after business rules |
| approval_required | BOOLEAN | Whether approval was required |
| started_at | TIMESTAMP | Workflow start time |
| completed_at | TIMESTAMP | Workflow completion time |

---

## 3. approvals

Stores human approval requests and decisions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| workflow_execution_id | UUID | Related workflow execution |
| approval_status | VARCHAR | Pending, approved, rejected |
| approver_email | VARCHAR | Approver identity |
| reason | TEXT | Reason approval was required |
| decision_notes | TEXT | Notes from approver |
| requested_at | TIMESTAMP | Approval request time |
| decided_at | TIMESTAMP | Approval decision time |

---

## 4. notifications

Tracks Slack and email notifications.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| workflow_execution_id | UUID | Related workflow execution |
| notification_type | VARCHAR | Slack or email |
| recipient | VARCHAR | Notification recipient |
| subject | TEXT | Notification subject |
| message | TEXT | Notification message |
| delivery_status | VARCHAR | Sent, failed, pending |
| error_message | TEXT | Failure details |
| sent_at | TIMESTAMP | Notification time |

---

## 5. audit_logs

Stores the complete workflow audit trail.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| workflow_execution_id | UUID | Related workflow execution |
| event_type | VARCHAR | Type of event |
| event_details | JSONB | Structured event details |
| created_at | TIMESTAMP | Event timestamp |

---

## 6. business_rules

Stores configurable workflow rules.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| rule_name | VARCHAR | Rule name |
| rule_type | VARCHAR | Priority, routing, approval, escalation |
| condition | JSONB | Rule condition |
| action | JSONB | Rule action |
| is_active | BOOLEAN | Whether rule is enabled |
| created_at | TIMESTAMP | Rule creation time |
| updated_at | TIMESTAMP | Rule update time |

---

## Entity Relationships

```text
tickets
   │
   └── workflow_executions
            │
            ├── approvals
            ├── notifications
            └── audit_logs

business_rules
   └── evaluated during workflow execution
```

---

## Design Decisions

### Store AI Recommendations and Final Decisions

The database stores both AI-generated recommendations and final business rule decisions.

This allows NorthStar Retail to compare what the AI recommended against what the workflow ultimately decided.

This supports auditability, troubleshooting, AI evaluation, and future workflow improvements.

---

### Separate Audit Logs from Tickets

Audit logs are stored separately from tickets because they represent workflow events over time.

A ticket is the business entity. An audit log is a historical event.

Separating them preserves workflow history without overloading the ticket table.

---

### Use JSONB for Flexible Rule and Event Data

The `business_rules` and `audit_logs` tables use JSONB fields for flexible structured data.

This allows the platform to store different rule conditions, rule actions, and event details without requiring a new database column for every workflow variation.

---

## Version 1 Scope

The Version 1 database does not include:

- User profile management
- Advanced role-based permissions
- Multi-tenant organization support
- Custom dashboard preferences
- Long-term AI training datasets
- Full Jira data replication

These items are outside the initial database scope.