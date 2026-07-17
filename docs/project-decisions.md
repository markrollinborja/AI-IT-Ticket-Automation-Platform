# Project Decisions

## Decision #1

Project Type:
Enterprise Internal Tool

Reason:
Matches the operational needs of NorthStar Retail.

---

## Decision #2

Primary Ticketing Platform:
Jira

Reason:
Industry-standard ticketing platform with mature APIs and webhook support.

---

## Decision #3

AI Role:
AI provides recommendations while deterministic business rules make workflow decisions.

Reason:
Keeps humans in control of business-critical decisions.

---

## Decision #4

Integration Trigger:
Jira Webhook

Reason:
Webhooks provide an event-driven integration pattern that more closely resembles enterprise automation systems than scheduled polling.

## Decision #5

Architecture Style:
Modular Monolith

Reason:
A modular monolith provides the fastest path to a deployable Version 1 while still supporting clean separation of concerns. This avoids unnecessary microservice complexity while keeping the system organized around clear enterprise automation responsibilities.

## Decision #6

AI Recommendation Storage:
Store both AI recommendations and final business decisions.

Reason:
AI recommendations must be auditable separately from final workflow decisions. This allows NorthStar Retail to compare AI-generated classifications, priorities, routing suggestions, and confidence scores against deterministic business rule outcomes.

## Decision #7

Repository Structure:
Monorepo

Reason:
A monorepo keeps the backend, frontend, documentation, diagrams, Docker configuration, and tests in one place. This simplifies development, deployment, and GitHub review for Version 1.

## Decision #8

Frontend Delivery:
Server-rendered dashboard (Jinja2 + Bootstrap) instead of a separate React frontend.

Reason:
The original plan called for a separate React application talking to a REST API. That was scoped down during implementation: a server-rendered dashboard removes an entire second deployable, build pipeline, and API contract to design and maintain, without giving up any functionality this project actually needs. Revisit only if a future version needs a richer, more interactive UI than server-rendered templates can reasonably support.

## Decision #9

Approval Workflow Design:
Real pause (not a record-only flag), triggered by ticket category rather than reporter identity, gating only risk-that-can-wait (security-sensitive changes, financial/payroll access, software purchases) and never gating anything urgent, with a single generic "human approval required" outcome rather than department-specific approver roles.

Reason:
Approval only being useful as an audit record (without actually blocking automation) doesn't match how real approval gates work - "automation should never do that automatically" only holds if the workflow genuinely stops. So a gated workflow run holds back the Jira priority update and the completion notification until a human decides via `POST /workflow-runs/{id}/approve` or `/reject`, and Jira's priority is set to a "Pending" workflow-state value in the meantime so the ticket visibly reflects its state even outside this platform's own dashboard.

The category list changed after the first version shipped. It originally also gated production/business-wide outages and executive-impact requests, modeled directly on early sample scenarios. Testing it against a real Jira ticket exposed the problem: gating a Critical outage behind a human signature actively works against the reason it's Critical in the first place - the whole value of fast classification is a fast response, and "a manager should be aware" doesn't require blocking anything, since the Slack notification already covers awareness without needing to withhold the Jira update. Real ITSM practice draws this same line - ITIL's "emergency change" process exists specifically because incident response can't wait for a change advisory board. So the two categories were removed, leaving only ones where waiting genuinely costs nothing: a firewall port can stay closed for another hour, payroll access can wait for sign-off, a software purchase can wait for a budget check. Urgency and identity turned out to be the wrong signals for "should this wait"; only risk-that-can-wait is.

Approver roles are intentionally NOT differentiated (no separate "IT Manager" vs "Finance" routing) - modeling real department-based approval routing without real accounts or permissions behind it would look like enterprise RBAC without actually being one, which is worse than not having it.
