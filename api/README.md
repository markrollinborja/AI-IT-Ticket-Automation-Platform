# AI IT Ticket Automation Platform

An enterprise-style IT ticket automation platform that automates IT ticket prioritization using a hybrid workflow of deterministic business rules and AI-powered classification.

Instead of sending every ticket to AI, the platform follows a rule-engine-first architecture. Known ticket patterns are handled instantly using deterministic rules, while only unmatched tickets are classified using OpenAI. This approach reduces AI cost, improves response time, and reflects how enterprise automation platforms are commonly designed.

The platform integrates with Jira Cloud through webhooks, updates ticket priorities automatically, records a complete workflow audit trail, sends Slack notifications, and provides a dashboard for monitoring workflow executions.

This project demonstrates enterprise workflow automation using modern backend engineering practices, third-party integrations, and AI-assisted decision making.

---

# System Architecture

The platform follows a **Jira-first, Rule Engine-first** architecture designed to mirror enterprise IT automation workflows.

<p align="center">
    <img src="diagrams/system-architecture.png" width="100%">
</p>

---

# Screenshots

## 1. Creating a Jira Ticket (Rule Engine)

The reporter creates a Jira ticket and selects an initial priority. The submitted priority is treated as user input and is automatically evaluated by the automation platform after the ticket is created.

![Creating Rule Engine Ticket](images/01-jira-create-rule-engine-ticket.png)

---

## 2. Creating a Jira Ticket (AI Classification)

Tickets that do not match deterministic business rules are routed to AI for classification.

![Creating AI Ticket](images/02-jira-create-ai-ticket.png)

---

## 3. Jira Project

Jira is the system of record. Every new ticket automatically triggers the automation workflow through a Jira webhook.

![Jira Ticket List](images/03-jira-ticket-list.png)

---

## 4. Workflow Operations Dashboard

The dashboard provides operational visibility into every workflow execution, including processing status, final priority, classification source, approval state, and execution history.

![Workflow Dashboard](images/04-workflow-dashboard.png)

---

## 5. Rule Engine Workflow

Deterministic tickets are classified immediately using predefined business rules without invoking AI.

![Rule Engine Workflow](images/05-workflow-details-rule-engine.png)

---

## 6. AI Workflow

When no deterministic rule matches, OpenAI classifies the ticket priority. The workflow records the AI-generated priority, confidence score, and complete execution history.

![AI Workflow](images/06-workflow-details-ai.png)

---

## 7. Slack Notification

After processing completes, the platform sends a formatted Slack notification containing the ticket details, final priority, classification source, and workflow completion time.

![Slack Notification](images/07-slack-notification.png)

---

## Tech Stack