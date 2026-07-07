# AI Classification Strategy

## Purpose

The AI classification service provides fallback ticket classification when deterministic business rules cannot confidently classify a Jira IT ticket.

The goal is not to replace business rules.

The goal is to support ambiguous or uncommon IT tickets while keeping the workflow auditable, predictable, and cost-conscious.

---

## Core Principle

Business rules always run first.

AI is only called when the Rule Engine returns no confident match.

```text
Jira Ticket
    ↓
Rule Engine
    ↓
Rule Match?
    ├── Yes → Use rule result and skip AI
    └── No  → Call AI classification service