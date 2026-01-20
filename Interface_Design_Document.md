# 🧩 Interface Design Document (IDD)

## 1. Purpose of the Document
This Interface Design Document (IDD) defines the **user interface structure, screen flows, and interaction patterns** for the Financial Planner App. It serves as a reference for developers, designers, and stakeholders during the **initial development phase**.

The goal is to ensure:
- Consistent UI/UX across the application
- Clear interaction between users and the AI-powered financial agent
- Smooth navigation and intuitive financial workflows

---

## 2. Design Principles
- **Clarity first:** Financial data should be easy to understand
- **Minimal cognitive load:** Fewer clicks, guided actions
- **AI-first UX:** Conversational interface as the primary interaction
- **Mobile-friendly:** Responsive by default
- **Trust & transparency:** Users must feel safe with their data

---

## 3. Target Users
- Students / early professionals
- Working professionals
- Family financial planners

(Refer to PRD for detailed personas)

---

## 4. Overall Navigation Structure

### Global Navigation (Post Login)
- Dashboard
- Chat (AI Financial Advisor)
- Expenses
- Budget
- Investments
- Profile

Navigation Style:
- Web: Left sidebar + top bar
- Mobile: Bottom navigation

---

## 5. Screen-by-Screen Interface Design

### 5.1 Login / Signup Screen
**Purpose:** User authentication

**UI Components:**
- Email input
- Password input
- Google OAuth button
- Login / Signup CTA

**Actions:**
- Validate credentials
- Redirect to onboarding

---

### 5.2 Onboarding & Persona Setup
**Purpose:** Collect initial financial context

**UI Components:**
- Age input
- Monthly income input
- Risk tolerance selector (Low / Medium / High)
- Financial goals (multi-select)

**Output:**
- User persona created
- Stored in agent memory

---

### 5.3 Dashboard Screen
**Purpose:** Financial snapshot at a glance

**UI Components:**
- Total monthly income
- Total expenses
- Remaining budget
- Savings ratio
- Quick insights cards

**Visuals:**
- Pie chart (expense distribution)
- Line chart (monthly spending trend)

---

### 5.4 AI Chat – Financial Advisor (Core Screen)
**Purpose:** Primary interaction point with the system

**UI Components:**
- Chat message list
- User input box
- Suggested prompts (chips)

**Example Prompts:**
- “Create a budget for this month”
- “Why am I overspending?”
- “Suggest investments for me”

**Behavior:**
- Agent reasons
- Calls tools
- Responds with actionable advice

---

### 5.5 Expense Management Screen
**Purpose:** Add, view, and manage expenses

**UI Components:**
- Add expense form (amount, category, date)
- Expense list (filter by month/category)
- Edit / delete actions

**Optional:**
- Voice or chat-based expense entry

---

### 5.6 Budget Planning Screen
**Purpose:** Plan and monitor category-wise budgets

**UI Components:**
- Category budget cards
- Progress bars
- Alerts for threshold breaches

**Actions:**
- Create / update budgets
- View utilization

---

### 5.7 Investment Planning Screen
**Purpose:** Display personalized investment strategy

**UI Components:**
- Risk profile summary
- Asset allocation chart
- Recommended instruments
- Expected returns (disclaimer included)

**Source:**
- Generated dynamically by AI agent

---

### 5.8 Profile & Settings Screen
**Purpose:** User preferences & controls

**UI Components:**
- Personal info
- Risk profile update
- Notification settings
- Logout

---

## 6. Interaction Flow Diagrams (Textual)

### Expense Tracking Flow
User → Add Expense → Validation → Save → Update Dashboard → Agent Insight

### Investment Advice Flow
User Query → Agent Reasoning → Persona Check → Tool Call → Response

---

## 7. Error & Empty States
- No expenses added → Show helpful tips
- Budget exceeded → Warning banner
- Network issue → Retry prompt

---

## 8. Accessibility & Usability
- Readable font sizes
- High contrast colors
- Keyboard navigation support
- Clear financial terminology

---

## 9. Security UI Considerations
- Masked sensitive data
- Session timeout handling
- Explicit consent for financial insights

---

## 10. Assumptions & Constraints
- Initial version supports manual data entry
- Chat-based interface prioritized over complex forms
- Investment insights are advisory, not legal advice

---

## 11. Future UI Enhancements
- Bank sync screens
- Tax planning dashboards
- Voice-based AI interaction
- Goal timelines

---

## 12. Conclusion
This IDD establishes a **clear, scalable, and AI-first interface foundation** for the Financial Planner App. It aligns closely with the PRD and supports iterative development from MVP to full-scale product.

🚀 Designed for clarity. Built for intelligence.

