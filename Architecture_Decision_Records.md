# 📐 ADR.md – Architecture Decision Records

This document captures the **key architectural decisions** made during the design of the **Financial Planner App (ADK-based)**. Each decision explains **what was decided, why it was chosen, and the trade-offs involved**.

The goal is to provide clarity for future contributors and reviewers, and to justify technical choices made early in the project lifecycle.

---

## ADR-001: Adopt an Agent-First Architecture (Google ADK)

### Status
Accepted

### Context
The application requires:
- High personalization (persona-based finance advice)
- Dynamic decision-making (budgeting, investments)
- Conversational user interaction

A traditional rule-based backend would be rigid and difficult to scale for intelligent behavior.

### Decision
Use **Google Agent Development Kit (ADK)** as the core architecture, where:
- AI agents handle reasoning and orchestration
- Backend APIs act as callable tools
- Business logic is driven by agent decisions, not static flows

### Consequences
**Pros:**
- High flexibility and personalization
- Easier to add new financial use cases (tax, loans, goals)
- Future-proof AI-first design

**Cons:**
- Higher initial learning curve
- Requires careful prompt and tool design

---

## ADR-002: Single Primary Financial Agent with Specialized Tools

### Status
Accepted

### Context
Multiple finance-related actions (expenses, budgets, investments) need coordination. Creating multiple agents initially would increase complexity.

### Decision
Implement:
- One **primary FinancialPlannerAgent**
- Multiple domain-specific tools (expense, budget, investment)

Persona reasoning is handled via a lightweight sub-agent or memory module.

### Consequences
**Pros:**
- Simpler orchestration
- Easier debugging and iteration
- Clear ownership of decisions

**Cons:**
- Agent prompt may grow large over time

---

## ADR-003: Thin Backend APIs, Logic in Agent + Tools

### Status
Accepted

### Context
Traditional backends often duplicate logic across endpoints. In an agentic system, this leads to inconsistency.

### Decision
Design backend APIs as **thin wrappers**:
- `/agent/chat` for all conversational flows
- CRUD logic encapsulated inside ADK tools

### Consequences
**Pros:**
- Clean separation of concerns
- Backend remains simple and maintainable

**Cons:**
- More responsibility on agent reasoning quality

---

## ADR-004: PostgreSQL as Primary Database

### Status
Accepted

### Context
The app manages structured financial data:
- Users
- Expenses
- Budgets
- Investment plans

Strong consistency and relational integrity are required.

### Decision
Use **PostgreSQL** as the primary database with SQLAlchemy ORM.

### Consequences
**Pros:**
- ACID compliance
- Strong querying and analytics support
- Industry-standard for financial data

**Cons:**
- Slightly heavier than NoSQL for simple use cases

---

## ADR-005: Agent Memory for Persona & Context Retention

### Status
Accepted

### Context
Personalized financial advice requires remembering:
- Risk profile
- Financial goals
- Past behavior

Stateless APIs would degrade user experience.

### Decision
Introduce an **agent memory layer**:
- Short-term conversation context
- Long-term persona attributes stored in DB

### Consequences
**Pros:**
- More human-like interaction
- Better recommendations over time

**Cons:**
- Requires memory cleanup and versioning strategy

---

## ADR-006: FastAPI for Tool & API Layer

### Status
Accepted

### Context
The backend must expose APIs that are:
- Fast
- Type-safe
- Easy to integrate with ADK tools

### Decision
Use **FastAPI** for the backend service layer.

### Consequences
**Pros:**
- Automatic API docs (Swagger)
- Async support
- Clean Python typing

**Cons:**
- Slight learning curve for async patterns

---

## ADR-007: Chat-Centric User Interface

### Status
Accepted

### Context
Financial planning involves decision-making, not just form filling. Conversational UX lowers user friction.

### Decision
Make **AI chat the primary interface**, supported by dashboards and forms.

### Consequences
**Pros:**
- Intuitive user experience
- High engagement

**Cons:**
- Requires strong prompt and fallback design

---

## ADR-008: Dockerized Development & Deployment

### Status
Accepted

### Context
Consistency across developer environments and deployments is critical.

### Decision
Use **Docker and Docker Compose** for:
- Backend
- Database
- Local development

### Consequences
**Pros:**
- Environment parity
- Easy onboarding

**Cons:**
- Slight overhead for small local changes

---

## ADR-009: Security-First by Design

### Status
Accepted

### Context
The app handles sensitive financial data.

### Decision
Adopt:
- JWT-based authentication
- Encrypted passwords
- HTTPS-only communication
- Explicit UI disclaimers for advisory content

### Consequences
**Pros:**
- Increased user trust
- Compliance readiness

**Cons:**
- Additional implementation effort

---

## ADR-010: Phased AI & Feature Rollout

### Status
Accepted

### Context
Building all intelligent features at once increases risk.

### Decision
Adopt a **phased approach**:
- Phase 1: Expense tracking + budgeting
- Phase 2: Investment planning + persona memory
- Phase 3: Advanced analytics & simulations

### Consequences
**Pros:**
- Faster MVP
- Easier validation

**Cons:**
- Requires careful roadmap management

---

## 📌 Final Notes
These ADRs are **living documents**. Any major architectural change must add a new ADR rather than modifying existing decisions.

This ensures transparency, accountability, and long-term maintainability of the Financial Planner App architecture.

🚀 Built to scale. Designed to evolve.

