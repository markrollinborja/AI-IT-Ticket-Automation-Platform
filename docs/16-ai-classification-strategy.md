# AI Classification Strategy

## Overview

The AI IT Ticket Automation Platform uses a hybrid classification strategy that combines deterministic business rules with AI-powered classification.

Rather than sending every ticket to an AI model, the platform executes a Rule Engine first and only uses OpenAI when deterministic rules cannot classify the ticket.

This approach improves performance, reduces operational cost, and reflects common enterprise automation patterns.

---

# Classification Workflow

```text
Incoming Jira Ticket
          │
          ▼
     Rule Engine
          │
   ┌──────┴──────┐
   │             │
Matched      No Match
   │             │
   ▼             ▼
Rule Result   OpenAI
      └──────┬──────┘
             ▼
      Final Priority
```

---

# Why Rule Engine First?

Deterministic rules are preferred whenever possible because they are:

- Faster
- Less expensive
- Predictable
- Easy to test
- Easy to audit

Many IT support tickets follow well-defined business patterns that do not require AI.

Examples include:

- Password reset requests
- VPN access issues
- Account lockouts
- Printer problems
- Software installation requests

These tickets can be classified immediately without consuming AI resources.

---

# AI Fallback Strategy

If the Rule Engine cannot classify a ticket, the platform sends the ticket title and description to OpenAI.

The model analyzes the ticket and returns:

```json
{
    "priority": "high",
    "confidence_score": 0.95
}
```

The workflow then:

1. Stores the AI priority.
2. Stores the confidence score.
3. Uses the AI priority as the final priority.
4. Updates Jira.
5. Records the workflow execution.

---

# Scope of AI in Version 1

AI is intentionally limited to **priority classification only**.

The platform does **not** use AI for:

- Category prediction
- Support team recommendation
- Suggested responses
- Missing information detection
- Approval decisions
- Ticket resolution

Keeping the AI scope focused reduces complexity while providing meaningful business value.

---

# Confidence Score

The confidence score is persisted for visibility and auditing.

It allows administrators to review AI outputs and compare AI confidence across workflow executions.

The confidence score does **not** influence business logic in Version 1.

---

# Design Principles

The AI strategy follows these principles:

- Rule Engine before AI
- AI only when necessary
- Deterministic behavior whenever possible
- Cost-efficient AI usage
- Transparent workflow execution
- Full auditability

---

# Benefits

This hybrid approach provides several advantages:

- Reduced OpenAI usage costs
- Faster average workflow execution
- Predictable handling of common tickets
- Better operational visibility
- Easier debugging and auditing
- Enterprise-ready architecture

---

# Future Improvements (Version 2)

Potential future AI capabilities include:

- Category classification
- Support team recommendation
- Suggested responses
- Ticket summarization
- Similar ticket detection
- Knowledge base recommendations

These enhancements are intentionally excluded from Version 1 to maintain a focused MVP.