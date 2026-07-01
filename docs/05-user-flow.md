# User Flow

## Overview

This document describes the end-to-end workflow of the AI IT Ticket Automation Platform.

The workflow begins when an employee submits an IT support ticket through Jira and ends when the ticket has been analyzed, processed, audited, and made available for administrators through the platform dashboard.

The objective of this workflow is to reduce manual ticket triage while maintaining human oversight for business-critical decisions.

---

# High-Level Workflow

![User Flow](../diagrams/user-flow-v1.png)

---

# Workflow Steps

## Step 1 — Employee Creates Ticket

An employee submits an IT support request through Jira.

The ticket contains information such as:

- Title
- Description
- Reporter
- Attachments (optional)

---

## Step 2 — Jira Sends Webhook

Jira immediately sends a webhook event to the AI IT Ticket Automation Platform whenever a new ticket is created.

The platform validates the request before processing begins.

---

## Step 3 — Ticket Validation

The platform validates:

- Webhook authenticity
- Required ticket fields
- Supported event type

Invalid requests are rejected and logged.

---

## Step 4 — Ticket Storage

The platform stores the ticket metadata before any workflow processing occurs.

This ensures all workflow activities can be audited later.

---

## Step 5 — AI Analysis

The AI service analyzes the ticket and generates:

- Ticket category
- Priority recommendation
- Support team recommendation
- Missing information (if applicable)
- Suggested first response

---

## Step 6 — Business Rules Engine

Business rules evaluate the AI recommendations.

Examples include:

- Executive users require approval.
- Security incidents are escalated immediately.
- Critical outages notify Infrastructure teams.
- Password reset requests bypass approval.

Business rules always have the final decision.

---

## Step 7 — Human Approval (If Required)

If business rules require approval:

- An approval request is generated.
- Stakeholders are notified.
- Workflow execution pauses until a decision is received.

If approval is not required, processing continues automatically.

---

## Step 8 — Notifications

The platform sends workflow notifications through:

- Slack
- Email

Notification recipients depend on workflow outcomes and business rules.

---

## Step 9 — Audit Logging

Every workflow action is recorded, including:

- AI recommendations
- Business rule decisions
- Approval outcomes
- Notifications
- Errors
- Processing timestamps

This provides complete traceability.

---

## Step 10 — Dashboard Update

The dashboard displays:

- Current ticket status
- Workflow progress
- Approval status
- Assigned support team
- Processing history
- Workflow metrics

Administrators can monitor workflow execution in real time.

---

# Workflow Completion

The workflow is considered complete when:

- The ticket has been analyzed.
- Business rules have been applied.
- Required approvals have been completed.
- Notifications have been delivered.
- Audit logs have been recorded.
- The dashboard reflects the latest workflow status.