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
