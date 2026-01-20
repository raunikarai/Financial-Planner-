# 🏗️ System Architecture Diagram – Financial Planner App (ADK-based)

## 1. Purpose
This document provides a **one-page system architecture overview** of the Financial Planner App. It illustrates the **high-level components, data flow, and interaction between the user interface, AI agents, backend services, and data stores**.

This diagram is intended for:
- Initial design approval
- Architecture reviews
- Academic / project submissions

---

## 2. High-Level Architecture Overview

The system follows an **Agent-First Architecture**, where the AI agent (built using Google ADK) is responsible for reasoning, orchestration, and decision-making. Traditional backend services act as **tools** callable by the agent.

---

## 3. System Architecture Diagram (Logical View)

```
┌──────────────────────┐
│        User          │
│  (Web / Mobile UI)   │
└──────────┬───────────┘
           │ HTTPS
           ▼
┌──────────────────────┐
│      Frontend        │
│  (React / Next.js)   │
│                      │
│ • Dashboard UI       │
│ • Expense Screens    │
│ • Chat Interface     │
└──────────┬───────────┘
           │ REST / WebSocket
           ▼
┌────────────────────────────────────┐
│        Backend API Layer            │
│            (FastAPI)                │
│                                    │
│ • /agent/chat                       │
│ • /auth                             │
│ • /health                           │
└──────────┬─────────────────────────┘
           │ Agent Invocation
           ▼
┌────────────────────────────────────┐
│     Google ADK Agent Runtime        │
│ (FinancialPlannerAgent)             │
│                                    │
│ • Intent understanding              │
│ • Persona reasoning                 │
│ • Tool orchestration                │
│ • Response generation               │
└──────────┬─────────────────────────┘
           │ Tool Calls
           ▼
┌────────────────────────────────────┐
│        Tool Layer (Backend)         │
│                                    │
│ • Expense Tools                     │
│ • Budget Tools                      │
│ • Investment Tools                  │
│ • User/Profile Tools                │
└──────────┬─────────────────────────┘
           │ DB Operations
           ▼
┌────────────────────────────────────┐
│        Data Storage Layer           │
│                                    │
│ • PostgreSQL (Primary DB)           │
│ • Redis (Cache)                     │
│ • Vector Store (Optional)           │
└────────────────────────────────────┘
```

---

## 4. Component Description

### 4.1 User Interface Layer
- Web or mobile application
- Provides dashboards, forms, and chat UI
- No business logic; purely presentation

---

### 4.2 Frontend Application
- Built using React / Next.js
- Handles routing, state management, and API communication
- Sends all conversational inputs to `/agent/chat`

---

### 4.3 Backend API Layer (FastAPI)
- Acts as a thin API gateway
- Handles authentication and request validation
- Forwards user messages to the ADK agent

---

### 4.4 AI Agent Layer (Google ADK)
- Core intelligence of the system
- Interprets user intent
- Maintains conversational and persona context
- Decides which backend tools to invoke

---

### 4.5 Tool Layer
- Encapsulates all business operations
- Each tool performs a single responsibility
- Examples: add expense, analyze budget, generate investment plan

---

### 4.6 Data Storage Layer
- **PostgreSQL:** Stores users, expenses, budgets, investments
- **Redis:** Caches frequent queries and session data
- **Vector Store (Optional):** Stores embeddings for long-term memory

---

## 5. Request Flow Example (Expense Entry)

1. User enters expense via chat or form
2. Frontend sends request to `/agent/chat`
3. FinancialPlannerAgent interprets intent
4. Agent calls `add_expense` tool
5. Tool writes data to PostgreSQL
6. Agent returns confirmation + insight
7. UI updates dashboard

---

## 6. Non-Functional Considerations
- **Security:** JWT auth, HTTPS, encrypted secrets
- **Scalability:** Stateless APIs, horizontally scalable agent runtime
- **Observability:** Logging and metrics at API and agent levels

---

## 7. Summary
This system architecture ensures:
- Strong separation of concerns
- AI-driven decision making
- Scalable and maintainable design

The architecture is optimized for **personalized financial planning**, **agent-based workflows**, and **future feature expansion**.

🚀 One-page. Clear. Review-ready.