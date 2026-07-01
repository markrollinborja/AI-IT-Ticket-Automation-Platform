# Folder Structure

## Overview

The AI IT Ticket Automation Platform uses a monorepo structure.

The repository contains the backend application, frontend application, project documentation, Docker configuration, and automated tests.

This structure keeps the project organized while simplifying development and deployment.

---

# Repository Structure

```text
ai-it-ticket-automation-platform/

│
├── backend/
│
├── frontend/
│
├── docs/
│
├── diagrams/
│
├── docker/
│
├── tests/
│
├── .env.example
│
├── .gitignore
│
├── docker-compose.yml
│
├── README.md
│
└── LICENSE
```

---

# Backend

```text
backend/

├── app/
│
├── api/
│
├── core/
│
├── models/
│
├── schemas/
│
├── services/
│
├── integrations/
│
├── database/
│
├── middleware/
│
├── utils/
│
└── main.py
```

---

# Frontend

```text
frontend/

├── src/
├── public/
├── components/
├── pages/
├── services/
├── hooks/
├── assets/
└── package.json
```

---

# Documentation

```text
docs/

01-business-problem.md

02-functional-requirements.md

03-non-functional-requirements.md

04-mvp-definition.md

05-user-flow.md

06-system-architecture.md

07-database-design.md

08-api-design.md

09-authentication-strategy.md

10-error-handling-strategy.md

11-logging-strategy.md

12-security-review.md

13-folder-structure.md
```

---

# Diagrams

```text
diagrams/

user-flow-v1.png

system-architecture.png

database-erd.png

deployment-diagram.png
```

---

# Docker

```text
docker/

Dockerfile.backend

Dockerfile.frontend
```

---

# Tests

```text
tests/

backend/

frontend/
```

---

# Design Principles

The repository structure follows these principles:

- Keep frontend and backend separated.
- Keep documentation alongside the source code.
- Keep diagrams in a dedicated directory.
- Organize backend code by responsibility.
- Keep deployment configuration isolated.
- Support future project growth without restructuring.

---

# Design Decision

Version 1 uses a monorepo because it simplifies development, deployment, documentation, and onboarding while remaining appropriate for the project's size.