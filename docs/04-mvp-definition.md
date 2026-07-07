# MVP Definition

## Overview

The Minimum Viable Product (MVP) defines the first production-ready release of the AI IT Ticket Automation Platform.

The objective of Version 1 is to automate IT ticket prioritization using a hybrid workflow that combines deterministic business rules with AI-powered classification. The system emphasizes enterprise architecture, auditability, and cost-efficient AI usage while remaining simple enough to demonstrate production-ready engineering practices.

---

# Version 1 Scope

The following capabilities are included in the MVP.

| Capability | Description |
|------------|-------------|
| Jira Cloud Integration | Receive new Jira issues through webhooks. |
| Jira-first Architecture | Jira is the source of truth. The application never creates Jira tickets. |
| Rule Engine | Deterministically classify ticket priority whenever possible. |
| OpenAI Fallback Classification | Use GPT-4o-mini only when no rule matches. |
| Priority Classification | AI classifies ticket priority only. |
| Workflow Tracking | Record each workflow execution using WorkflowRun. |
| Audit Logging | Record important workflow events for traceability. |
| Jira Priority Updates | Automatically synchronize the final priority back to Jira. |
| Slack Notifications | Notify Slack when workflows complete or fail. |
| Dashboard | Monitor workflow executions and view workflow details. |
| Docker Support | Containerized local development using Docker Compose. |

---

# AI Scope

Version 1 intentionally limits AI to **priority classification only**.

The AI returns:

```json
{
  "priority": "high",
  "confidence_score": 0.95
}
```

The confidence score is stored as audit metadata and does not influence business logic.

---

# Rule Engine Strategy

The Rule Engine always executes before AI.

Benefits include:

- Faster execution
- Lower OpenAI costs
- Predictable behavior
- Easier testing
- Easier auditing

AI is used only when deterministic rules cannot classify the ticket.

---

# Out of Scope (Version 2)

The following features are intentionally excluded from Version 1:

- AI category classification
- Support team recommendation
- Suggested responses
- Human approval workflows
- Email notifications
- Analytics and reporting
- Role-based authentication

These features are reserved for future versions to keep the MVP focused and production-ready.

---

# MVP Success Criteria

Version 1 is considered complete when the platform can:

- Receive Jira webhook events
- Persist incoming tickets
- Execute the Rule Engine
- Use OpenAI only when necessary
- Update Jira priorities automatically
- Record WorkflowRun and AuditLog history
- Send Slack notifications
- Display workflow execution history through the dashboard