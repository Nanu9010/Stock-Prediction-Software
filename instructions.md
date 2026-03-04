# 🤖 AGENT OPERATING INSTRUCTIONS
## 3-Layer Architecture Execution Protocol

> **This file is the operating constitution for any AI agent building software.**
> Every task MUST pass through all 3 layers — in order — no exceptions.

---

## 🏗️ THE 3-LAYER ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1 — UNDERSTAND          [ WHAT TO DO ]               │
│  LAYER 2 — DECIDE              [ HOW TO DO IT ]             │
│  LAYER 3 — EXECUTE             [ DO THE WORK ]              │
└─────────────────────────────────────────────────────────────┘
```

Skipping a layer or merging layers is a protocol violation.
It produces brittle, unscalable, undebuggable outputs.

---

## LAYER 1 — UNDERSTAND ("What to Do")

### Purpose
Before writing a single line of code or planning a single component,
the agent MUST fully understand the problem space.

### Mandatory Actions
- Parse the user's request and extract the **core intent**
- Identify what is **explicitly stated** vs what is **implied**
- List all **unknowns, ambiguities, and edge cases**
- Define the **scope boundary** — what is IN scope and what is OUT
- Identify the **actor** (who uses this?) and the **trigger** (what starts the process?)
- Map out **expected inputs** and **expected outputs**

### Questions to Answer Before Leaving Layer 1
```
1. What problem does this solve?
2. Who is the user/consumer of this system?
3. What are the success criteria?
4. What are the failure conditions?
5. What data flows IN and what data flows OUT?
6. Are there any compliance, security, or performance constraints?
```

### Output of Layer 1
A clear, written **Problem Definition Document** — even if it's 5 bullet points.
No ambiguity should survive Layer 1.

### ⚠️ Anti-Patterns to Avoid
- Jumping to tech stack before understanding the problem
- Assuming what the user means without verifying
- Ignoring edge cases because they seem unlikely
- Treating the feature request as the full requirement

---

## LAYER 2 — DECIDE ("How to Do It")

### Purpose
Design the architecture, choose the tools, and plan the folder structure
BEFORE touching any file or writing any implementation code.

### Mandatory Actions
- Choose the **tech stack** with reasoning (not preference)
- Define the **folder structure** (see Folder Structure Protocol below)
- Map out **data models / schemas**
- Define all **API contracts** (endpoints, request/response shapes)
- Identify **third-party dependencies** and justify each one
- Define **environment separation** (dev / staging / prod concerns)
- Anticipate **failure points** and define how they'll be handled
- Write **pseudocode or flow diagrams** for non-trivial logic

### Questions to Answer Before Leaving Layer 2
```
1. What is the separation of concerns across layers?
2. How does data flow from frontend → backend → database?
3. What are the API contracts between frontend and backend?
4. Where can this design fail under load or bad input?
5. What will be hardest to change later — and have I designed for it?
6. Is this the simplest design that solves the problem correctly?
```

### Output of Layer 2
- Folder structure (written out explicitly)
- API contract list
- Data model definitions
- Dependency list with justification
- Known risks and mitigation plan

### ⚠️ Anti-Patterns to Avoid
- Choosing a framework because it's trendy — choose it because it fits
- Over-engineering for scale that doesn't exist yet
- Under-engineering so that the first real-world change breaks everything
- Mixing frontend logic into backend, or DB logic into API handlers
- Undefined error states

---

## LAYER 3 — EXECUTE ("Do the Work")

### Purpose
Implement exactly what was designed in Layer 2. Not more. Not less.
Every file created must trace back to a decision made in Layer 2.

### Mandatory Actions
- Follow the **folder structure** defined in Layer 2 strictly
- Write **production-quality code** — not prototype, not tutorial code
- Every function must have a **single responsibility**
- Every external call (DB, API, file system) must have **error handling**
- No hardcoded secrets, credentials, or environment-specific values in code
- All environment config must live in **`.env` files** (never committed)
- Write at minimum **stub comments** for complex logic explaining WHY, not WHAT
- Validate all **inputs at the boundary** (API layer, not deep in business logic)

### Code Quality Checklist
```
[ ] No hardcoded values — use environment variables or constants
[ ] Functions are small and do one thing
[ ] Error paths are handled explicitly (not silently swallowed)
[ ] Naming is clear — no single-letter variables outside loops
[ ] No dead code committed
[ ] Database queries are parameterized (no SQL injection vectors)
[ ] API responses have consistent shape (success and error)
[ ] Sensitive data is never logged
```

### ⚠️ Anti-Patterns to Avoid
- Writing business logic inside route handlers / controllers
- Mixing database access with HTTP response logic
- Returning raw DB errors to the client
- Using `any` type in TypeScript without justification
- Not handling async errors (unhandled promise rejections)
- Putting secrets in code or `.env.example` with real values

---

## 📁 MANDATORY FOLDER STRUCTURE PROTOCOL

Every project MUST be separated into at minimum 3 distinct folders:

```
project-root/
│
├── frontend/                   # ALL UI concerns live here
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route-level page components
│   │   ├── hooks/              # Custom React/framework hooks
│   │   ├── services/           # API call functions (axios/fetch wrappers)
│   │   ├── store/              # State management (Redux, Zustand, etc.)
│   │   ├── utils/              # Pure helper functions
│   │   └── types/              # Shared type definitions
│   ├── public/
│   ├── .env.local
│   └── package.json
│
├── backend/                    # ALL server/business logic lives here
│   ├── src/
│   │   ├── routes/             # Route definitions only — no logic
│   │   ├── controllers/        # Request handling — thin layer
│   │   ├── services/           # Business logic — the core of your app
│   │   ├── middlewares/        # Auth, logging, error handling, validation
│   │   ├── models/             # Data model definitions (ORM or plain)
│   │   ├── utils/              # Pure helper functions
│   │   ├── config/             # App configuration and env parsing
│   │   └── types/              # TypeScript types / interfaces
│   ├── .env
│   ├── .env.example            # Template with NO real values
│   └── package.json
│
├── database/                   # ALL database concerns live here
│   ├── migrations/             # Version-controlled schema changes
│   ├── seeds/                  # Initial/test data population scripts
│   ├── schemas/                # Schema definitions (SQL or ORM schema files)
│   └── README.md               # How to run migrations and seeds
│
├── docs/                       # Architecture decisions, API docs, diagrams
├── .gitignore
└── README.md                   # How to run the entire project
```

### Why This Separation Matters
- **Frontend** changes (UI redesign) must NEVER require backend changes
- **Backend** changes (new endpoint) must NEVER touch database migration files
- **Database** changes (schema migration) must be trackable, versioned, and reversible
- Each layer can be **deployed independently**, **tested independently**, and **scaled independently**
- New team members can own a single folder without breaking others

---

## 🔁 LAYER COMMUNICATION RULES

```
Frontend  ──(HTTP/REST/GraphQL)──►  Backend  ──(ORM/Query)──►  Database
    ▲                                   │                           │
    └────────(JSON Response)────────────┘                           │
                                        ▲                           │
                                        └──────(Result Set)─────────┘
```

**Hard Rules:**
1. Frontend NEVER talks to the database directly
2. Backend NEVER returns raw database errors to the client
3. Database NEVER contains business logic (no stored procedures for app logic)
4. API contracts are defined in Layer 2, not discovered during Layer 3

---

## 🛡️ SECURITY OPERATING PRINCIPLES

These are non-negotiable regardless of project size:

```
1. NEVER store plaintext passwords — always hash (bcrypt / argon2)
2. NEVER trust user input — validate and sanitize at every entry point
3. NEVER expose stack traces or internal errors to the client
4. NEVER commit .env files — always use .env.example as template
5. ALWAYS use parameterized queries — never string-concatenate SQL
6. ALWAYS use HTTPS in production
7. ALWAYS set CORS policies explicitly — never use wildcard in production
8. ALWAYS expire tokens — no infinite session/JWT lifetimes
```

---

## ⚡ PERFORMANCE OPERATING PRINCIPLES

```
1. Database queries MUST be analyzed before going to production
   → No N+1 queries. Use joins or eager loading.

2. API responses MUST be paginated for list endpoints
   → Never return unbounded arrays

3. Heavy computation MUST be moved out of the request/response cycle
   → Use background jobs / queues

4. Repeated expensive operations MUST be cached
   → Identify cache keys, TTLs, and invalidation strategy upfront

5. Frontend MUST NOT make redundant API calls
   → Implement request deduplication or React Query / SWR patterns
```

---

## 📋 PRE-EXECUTION CHECKLIST (Run Before Starting Layer 3)

Before writing a single file, verify:

```
[ ] Problem is fully understood (Layer 1 complete)
[ ] Architecture is designed (Layer 2 complete)
[ ] Folder structure is defined
[ ] API contracts are written
[ ] Data models are defined
[ ] Environment variables are identified (not yet set — just named)
[ ] Security concerns are addressed in design
[ ] Failure scenarios have defined handling strategies
[ ] Tech stack is chosen with justification
```

If any box is unchecked — go back. Do not proceed to Layer 3.

---

## 🚨 CRITICAL FAILURE CONDITIONS

An agent has failed if any of the following occur:

```
✗ Code was written before the problem was understood
✗ Folder structure was created ad hoc during coding
✗ Business logic lives inside route handlers
✗ Database is accessed directly from frontend
✗ Hardcoded secrets or config values exist in source files
✗ Error handling is missing or swallows exceptions silently
✗ API response shape is inconsistent between endpoints
✗ A change to one layer requires changes in all 3 layers
✗ Migrations are missing — schema changes were made directly in DB
✗ The project cannot be run from a clean clone using README instructions alone
```

---Instructions 

## 📌 FINAL PRINCIPLE

> **Build systems, not scripts.**
> A script solves today's problem.
> A system solves today's problem AND tomorrow's variant of it.
> Every design decision must pass the test:
> *"If this requirement changes by 20%, how much of my code breaks?"*
> If the answer is "a lot" — your architecture has failed before it ran.

---

*This document governs all agent behavior. When in doubt, return to Layer 1.*