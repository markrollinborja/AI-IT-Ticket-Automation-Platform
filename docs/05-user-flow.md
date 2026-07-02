# User Flow

## Overview

This document describes the end-to-end workflow of the AI IT Ticket Automation Platform.

The workflow begins when an employee submits an IT support ticket through Jira and ends when the ticket has been analyzed, processed, audited, and made available for administrators through the platform dashboard.

The platform is designed to automate IT ticket triage while ensuring deterministic business rules always take precedence over AI recommendations. AI is only used when business rules cannot confidently classify a ticket.

---

# High-Level Workflow

![User Flow](../diagrams/user-flow-v1.png)

---

# Workflow Steps

## Step 1 — Employee Creates Ticket

An employee submits an IT support request through Jira.

The ticket may contain:

- Title
- Description
- Reporter
- Attachments (optional)

Jira becomes the system of record for the ticket throughout its lifecycle.

---

## Step 2 — Jira Sends Webhook

When a new ticket is created, Jira sends a webhook event to the AI IT Ticket Automation Platform.

The webhook contains the ticket information required for workflow processing.

---

## Step 3 — Ticket Validation

The platform validates the incoming webhook before processing begins.

Validation includes:

- Webhook authenticity
- Required ticket fields
- Supported event type

Invalid requests are rejected and logged.

---

## Step 4 — Workflow Record Creation

The platform creates a workflow record for the incoming Jira issue.

The workflow record tracks automation activities performed by the platform and is separate from the Jira ticket itself.

Typical information includes:

- Jira Issue Key
- Workflow Status
- Processing Timestamps
- Automation State

This enables workflow monitoring and auditing without duplicating Jira's ticket data.

---

## Step 5 — Business Rules Engine

The Business Rules Engine evaluates the ticket against predefined deterministic rules.

Examples include:

- Production outage
- VPN connectivity issue
- Password reset
- Access denied
- Other known IT support scenarios

If a matching rule is found:

- The priority is assigned immediately.
- AI analysis is skipped.
- Workflow processing continues.

If no matching rule is found:

- The ticket is forwarded to the AI Classification Service.

Business rules always have the highest priority when deterministic conditions are met.

---

## Step 6 — AI Analysis (Fallback)

The AI Classification Service analyzes tickets that cannot be classified by the Business Rules Engine.

The AI may generate:

- Ticket category
- Priority recommendation
- Support team recommendation
- Missing information
- Suggested first response

The AI assists the automation workflow but is only used for ambiguous or unknown ticket types.

---

## Step 7 — Human Approval (If Required)

Business policies determine whether human approval is required.

Examples include:

- Executive user requests
- Security-related incidents
- High-risk automation actions

If approval is required:

- An approval request is generated.
- Stakeholders are notified.
- Workflow execution pauses until a decision is received.

Otherwise, processing continues automatically.

---

## Step 8 — Notifications

The platform sends workflow notifications based on the final workflow outcome.

Notification channels may include:

- Slack
- Email

Notifications may include:

- Assigned support team
- Priority changes
- Approval requests
- Workflow completion
- Processing failures

---

## Step 9 — Audit Logging

Every significant workflow action is recorded.

Examples include:

- Rule Engine decisions
- AI recommendations (when used)
- Human approval outcomes
- Notifications sent
- Jira integration events
- Errors
- Processing timestamps

These audit logs provide complete traceability for every automation workflow.

---

## Step 10 — Dashboard Update

The platform dashboard displays workflow information in real time.

Examples include:

- Jira Issue Key
- Workflow Status
- Current Priority
- Classification Source (Rule Engine or AI)
- Approval Status
- Processing History
- Workflow Metrics

The dashboard provides administrators with visibility into workflow execution without replacing Jira as the ticket management system.

---

# Workflow Completion

The workflow is considered complete when:

- The Jira ticket has been processed.
- Business rules have been evaluated.
- AI analysis has completed (if required).
- Required approvals have been completed.
- Notifications have been delivered.
- Audit logs have been recorded.
- Workflow records have been updated.
- The dashboard reflects the latest workflow status.