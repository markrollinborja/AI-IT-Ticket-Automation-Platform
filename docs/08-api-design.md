# API Design

## Overview

The AI IT Ticket Automation Platform exposes REST APIs for enterprise integrations, workflow management, approvals, and dashboard operations.

The API follows RESTful principles and uses JSON for request and response payloads.

---

# API Base URL

```
/api/v1
```

Versioning allows future API enhancements without breaking existing integrations.

---

# Webhook Endpoints

## POST /api/v1/webhooks/jira

Receives ticket creation events from Jira.

**Purpose**

Starts the ticket automation workflow.

---

# Ticket Endpoints

## GET /api/v1/tickets

Returns all processed tickets.

---

## GET /api/v1/tickets/{ticket_id}

Returns detailed information for a single ticket.

---

# Workflow Endpoints

## GET /api/v1/workflows/{workflow_id}

Returns workflow execution details.

---

## POST /api/v1/workflows/{workflow_id}/retry

Retries a failed workflow execution.

---

# Approval Endpoints

## GET /api/v1/approvals

Returns pending approval requests.

---

## POST /api/v1/approvals/{approval_id}/approve

Approves a workflow.

---

## POST /api/v1/approvals/{approval_id}/reject

Rejects a workflow.

---

# Dashboard Endpoints

## GET /api/v1/dashboard/metrics

Returns dashboard summary metrics.

Example:

- Tickets Processed
- Pending Approvals
- Failed Workflows
- Average Processing Time

---

## GET /api/v1/dashboard/recent-activity

Returns recent workflow activity.

---

# Health Endpoint

## GET /api/v1/health

Returns application health status.

This endpoint is intended for monitoring and deployment verification.

---

# Authentication

All API endpoints require authentication except:

- GET /api/v1/health
- POST /api/v1/webhooks/jira (validated using webhook secrets)

Authentication details are defined in the Authentication Strategy document.

---

# Response Format

Successful responses use a consistent JSON structure.

```json
{
  "success": true,
  "data": {}
}
```

Error responses use:

```json
{
  "success": false,
  "error": {
    "code": "WORKFLOW_FAILED",
    "message": "Workflow execution failed."
  }
}
```

---

# API Design Principles

The API follows these principles:

- RESTful resource naming
- Versioned endpoints
- Consistent response structure
- JSON request and response bodies
- Stateless request handling
- Secure authentication
- Clear separation between workflow operations and administrative functions