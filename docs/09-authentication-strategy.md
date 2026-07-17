# Authentication Strategy

## Current Status: Not Implemented

There is no authentication in this project as of Version 2. Every endpoint — the API
routes, the dashboard, and the Jira webhook receiver — is open. This is a deliberate,
documented scope decision, not an oversight: see
[04-mvp-definition.md](04-mvp-definition.md), which lists "Role-based authentication" under
Out of Scope for Version 1, and [project-roadmap.md](project-roadmap.md), where
authentication is listed under Future Ideas.

This document describes the plan for when authentication is added, so the design is
thought through in advance rather than bolted on later.

---

## Why It's Deferred

Two reasons:

- **Nothing in this project's demo currently needs it.** It runs against a Jira Cloud
  sandbox and a single developer's local/deployed instance. There's no multi-user access to
  protect yet.
- **The Jira webhook problem is a signature validation problem, not a login problem.**
  Adding a `POST` bearer-token check to `/webhooks/jira` wouldn't actually secure it —
  Jira doesn't send a bearer token, it sends a webhook payload. Properly securing that
  endpoint means validating a Jira webhook signature/secret, which is a different piece of
  work than "add auth to the dashboard." Conflating the two was a mistake in earlier
  planning; this document previously described a single blanket "bearer token" strategy
  covering both, which wasn't realistic.

---

## Planned Approach (Future Work)

When authentication is added, it should be split into two separate concerns:

### 1. Dashboard / admin API authentication

Simple bearer-token authentication (a single shared token via FastAPI `Depends`, checked
against an environment variable) is enough for this project's scale. Something like:

```http
Authorization: Bearer <token>
```

Full OAuth/SSO/RBAC would be over-engineering for a single-operator internal tool — see
[12-security-review.md](12-security-review.md) for what's intentionally out of scope and
why.

### 2. Jira webhook validation

`POST /webhooks/jira` should validate that incoming requests actually came from Jira. Jira
Cloud webhooks don't include a bearer token; the realistic options are an IP allowlist (if
Jira publishes stable webhook source IPs) or a shared-secret query parameter/header checked
on every request. This is a separate task from dashboard auth and should be scoped and
implemented independently.

---

## What Exists Today Instead

Since there's no auth, the current safeguards are:

- The app is not deployed publicly yet (see [project-roadmap.md](project-roadmap.md),
  "Next Highest ROI Feature" — public deployment is the next step, and auth should be
  revisited before or shortly after that happens if the deployment is meant to stay up
  long-term).
- `/webhooks/jira` does validate payload structure and event type (see
  `app/services/jira_webhook_validation_service.py`), which rejects malformed requests —
  but this is input validation, not authentication. It does not verify the request came
  from Jira.

If this project is deployed publicly and left running, adding at least basic bearer-token
auth to the dashboard and a shared-secret check on the webhook endpoint should happen
before real Jira/Slack/OpenAI credentials are wired up against it.
