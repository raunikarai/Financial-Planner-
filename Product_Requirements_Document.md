# 📊 Financial Planner App – Product Requirements Document (PRD)

## 1. Product Overview
The **Financial Planner App** is a smart, AI-assisted personal finance platform that helps users:
- Plan and manage monthly budgets
- Track income and expenses in real time
- Get personalized investment strategies based on their financial persona
- Build healthy financial habits over time

The app targets individuals who want clarity, control, and confidence over their finances — without needing deep financial knowledge.

---

## 2. Goals & Objectives
### Primary Goals
- Help users understand where their money goes
- Enable smarter budgeting decisions
- Provide personalized investment guidance
- Improve financial discipline and long-term wealth planning

### Success Metrics
- Monthly active users (MAU)
- Budget adherence rate
- Expense categorization accuracy
- Investment plan adoption rate
- User retention (30/60/90 days)

---

## 3. User Personas

### Persona 1: The Student / Early Professional
**Age:** 18–25  
**Income:** Low to moderate  
**Goals:** Expense control, savings habit  
**Pain Points:** Overspending, no budgeting discipline  
**Key Features Used:** Budgeting, expense tracking

---

### Persona 2: The Working Professional
**Age:** 25–40  
**Income:** Stable monthly income  
**Goals:** Savings, investments, tax planning  
**Pain Points:** No time to plan finances  
**Key Features Used:** Investment planning, analytics, insights

---

### Persona 3: The Family Planner
**Age:** 35–55  
**Income:** High but with responsibilities  
**Goals:** Child education, retirement planning  
**Pain Points:** Managing multiple goals simultaneously  
**Key Features Used:** Goal-based planning, long-term investments

---

## 4. Core Features

### 4.1 Budget Planning
- Monthly income setup
- Category-wise budget allocation
- Alerts when nearing limits

### 4.2 Expense Tracking
- Manual expense entry
- Auto-categorization (ML-based)
- Daily / monthly summaries

### 4.3 Investment Planner
- Risk profiling questionnaire
- Personalized investment strategy
- Asset allocation suggestions (Equity, Debt, MF, FD)

### 4.4 Analytics & Insights
- Spending trends
- Savings ratio
- Investment growth projections

### 4.5 AI-Powered Financial Advisor (Phase 2)
- Chat-based financial guidance
- Budget improvement tips
- What-if simulations

---

## 5. Tech Stack

### Frontend
- **Web:** React.js / Next.js
- **Mobile (Optional):** Flutter / React Native
- **UI:** Tailwind CSS / Material UI

### Backend
- **Framework:** FastAPI / Flask
- **Auth:** JWT + OAuth (Google)
- **Business Logic:** Python

### AI / ML
- Persona classification (Scikit-learn / PyTorch)
- Expense categorization (NLP model)
- Recommendation engine

### Database
- **Primary DB:** PostgreSQL
- **Cache:** Redis

### Cloud & DevOps
- AWS / GCP
- Docker
- CI/CD (GitHub Actions)

---

## 6. Database Schema (High-Level)

### User Table
```sql
users (
  id UUID PRIMARY KEY,
  name VARCHAR,
  email VARCHAR UNIQUE,
  password_hash TEXT,
  age INT,
  income FLOAT,
  risk_profile VARCHAR,
  created_at TIMESTAMP
)
```

### Expense Table
```sql
expenses (
  id UUID PRIMARY KEY,
  user_id UUID,
  amount FLOAT,
  category VARCHAR,
  description TEXT,
  date DATE,
  created_at TIMESTAMP
)
```

### Budget Table
```sql
budgets (
  id UUID PRIMARY KEY,
  user_id UUID,
  category VARCHAR,
  monthly_limit FLOAT
)
```

### Investment Plan Table
```sql
investment_plans (
  id UUID PRIMARY KEY,
  user_id UUID,
  asset_type VARCHAR,
  allocation_percentage FLOAT,
  expected_return FLOAT
)
```

---

## 7. System Design (High-Level)

### Architecture
- Client → API Gateway → Backend Services
- Auth Service
- Finance Service
- AI Recommendation Service
- Database Layer

### Flow Example (Expense Tracking)
1. User adds expense
2. API validates & stores data
3. ML service categorizes expense
4. Budget service updates usage
5. User receives insights

---

## 8. API Endpoints

### Authentication
- `POST /auth/register`
- `POST /auth/login`

### User
- `GET /user/profile`
- `PUT /user/profile`

### Expenses
- `POST /expenses`
- `GET /expenses?month=`
- `DELETE /expenses/{id}`

### Budget
- `POST /budget`
- `GET /budget`

### Investments
- `POST /investment/plan`
- `GET /investment/recommendations`

---

## 9. Security & Compliance
- Encrypted passwords (bcrypt)
- HTTPS everywhere
- Role-based access control
- GDPR-ready data handling

---

## 10. Future Enhancements
- Bank account integration
- Tax optimization module
- Credit score tracking
- Voice-based financial assistant

---

## 11. Assumptions & Constraints
- Internet access required
- Initial version is manual data entry
- Investment advice is informational only

---

## 12. Final Note
This PRD is designed to be **scalable**, **AI-ready**, and **business-viable**, making it suitable for MVP development and future enterprise expansion.

🚀 Ready to build smart finance for the next generation.

