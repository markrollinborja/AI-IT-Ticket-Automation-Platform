# System Architecture

## Overview

The AI IT Ticket Automation Platform follows a **Jira-first, Rule Engine-first** architecture designed to mirror enterprise IT automation workflows.

Jira is the system of record for all tickets. The platform acts as an automation layer that receives Jira webhook events, classifies ticket priority, updates Jira, records workflow history, and notifies stakeholders.

---

# High-Level Architecture

```text
                        User
                          │
                          ▼
                 Jira Ticket Created
                          │
                          ▼
                   Jira Cloud Webhook
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
                  ┌────────┴────────┐
                  │                 │
          Rule Matched      No Rule Match
                  │                 │
                  │                 ▼
                  │        OpenAI (GPT-4o-mini)
                  │                 │
                  └────────┬────────┘
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

---

# Workflow Components

## Jira Cloud

Receives IT support requests and serves as the source of truth for all tickets.

---

## FastAPI

Receives Jira webhook events and coordinates the workflow execution.

---

## Workflow Service

Orchestrates the end-to-end ticket processing workflow, including persistence, classification, notifications, and workflow tracking.

---

## Rule Engine

Attempts to classify ticket priority using deterministic business rules.

This executes before AI to improve performance, reduce cost, and ensure predictable behavior.

---

## OpenAI Classification

If no rule matches, GPT-4o-mini classifies the ticket priority and returns:

```json
{
    "priority": "high",
    "confidence_score": 0.95
}
```

Only the priority is used for workflow decisions.

The confidence score is stored for auditing and visibility.

---

## WorkflowRun

Tracks each workflow execution, including:

- Workflow status
- Final priority
- Classification source
- AI metadata
- Start time
- Completion time
- Failure information

---

## Audit Logs

Records important workflow events such as:

- Workflow started
- Ticket classified
- Jira priority updated
- Workflow completed
- Workflow failed

---

## Slack

Sends workflow notifications after successful or failed executions.

---

# Design Principles

The architecture follows these principles:

- Jira remains the source of truth.
- Rule Engine executes before AI.
- AI is used only when deterministic rules cannot classify a ticket.
- Every workflow execution is traceable.
- Every significant event is auditable.
- External integrations remain loosely coupled through service classes.

---

# Version 1 Scope

The architecture intentionally limits AI to **priority classification only**.

Features such as category prediction, support team recommendation, approval workflows, and suggested responses are reserved for Version 2.