# Expense Tracker Backend

## Project Overview
This is a FastAPI backend for an expense tracking system with JWT-based authentication, role-based authorization, account management, and transaction tracking.

### What it does
- User registration and login with JWT access tokens
- Role-based access (`user`, `admin`)
- Account CRUD operations for authenticated users
- Transaction CRUD operations linked to accounts
- Admin endpoints to inspect and manage users, accounts, and transactions
- Rate limiting on auth endpoints
- Centralized exception handling and structured logging

Frontend is intentionally out of scope in this repo.

## Tech Stack
- FastAPI
- PostgreSQL
- Psycopg2
- JWT (`python-jose`)
- Bcrypt (password hashing)
- SlowAPI (rate limiting)
- Redis (optional cache)
- Docker
- Uvicorn

## Architecture
Layered flow:

`Router -> Service -> DB`

Responsibility split:
- Router Layer (`/routes`) handles HTTP, validation, and auth dependencies.
- Service Layer (`/Service`) holds business logic and orchestration.
- DB Utility (`/utils/db.py`) manages connection pooling and transaction handling.

Simple diagram:

```mermaid
flowchart LR
  "Client (Frontend/Postman)" --> "FastAPI Router"
  "FastAPI Router" --> "Service Layer"
  "Service Layer" --> "PostgreSQL"
  "FastAPI Router" --> "Auth & RBAC"
  "Auth & RBAC" --> "JWT"
```

## Setup (Local)

### 1. Clone
```bash
git clone https://github.com/Ritik2712/Expense-tracker-BE.git
cd Expense-tracker-BE
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env`
Use `.env.example` as reference:

```env
DB_NAME=finance_app
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=change-this-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Optional
REDIS_URL=redis://localhost:6379/0
```

### 4. Apply schema
```bash
psql -U postgres -d finance_app -f schema.sql
```

### 5. Run app
```bash
uvicorn main:app --reload
```

## Docker Run

### 1. Build app image
```bash
docker build -t expense-tracker-be .
```

### 2. Run PostgreSQL container (separate)
```bash
docker network create expense-net

docker run -d --name expense-postgres \
  --network expense-net \
  -e POSTGRES_DB=finance_app \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:17
```

### 3. Apply schema in DB container
```bash
docker exec -i expense-postgres psql -U postgres -d finance_app < schema.sql
```

### 4. Run backend container
```bash
docker run -d --name expense-tracker-be \
  --network expense-net \
  -p 8000:8000 \
  -e DB_NAME=finance_app \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e DB_HOST=expense-postgres \
  -e DB_PORT=5432 \
  -e SECRET_KEY='change-this-super-secret-key' \
  -e ALGORITHM=HS256 \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=60 \
  expense-tracker-be
```

## Environment Variables
Required:
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Optional:
- `APP_PORT` (default `8000`)
- `LOG_LEVEL` (default `INFO`)
- `REDIS_URL` (enables admin caching)

## API Overview

Auth:
- `POST /auth` - register user
- `POST /auth/admin` - register admin
- `POST /auth/login` - login

Users:
- `GET /users/me` - current user profile
- `PUT /users/update/{id}` - update own user
- `DELETE /users/{id}` - delete own user

Accounts:
- `POST /accounts` - create account
- `GET /accounts?page=1&limit=10` - list own accounts
- `PUT /accounts/{account_id}` - update own account
- `DELETE /accounts/{account_id}` - delete own account

Transactions:
- `POST /transactions` - create transaction
- `GET /transactions?account_id=<uuid>&page=1&limit=10` - list by account
- `GET /transactions/{transaction_id}?account_id=<uuid>` - get one
- `GET /transactions/user/all?page=1&limit=10` - list by user
- `PUT /transactions/{transaction_id}` - update transaction
- `DELETE /transactions/{transaction_id}` - delete transaction

Admin:
- `GET /admin/users?page=1&limit=10`
- `GET /admin/users/{user_id}`
- `DELETE /admin/users/{user_id}`
- `GET /admin/accounts?page=1&limit=10`
- `GET /admin/accounts/{account_id}`
- `DELETE /admin/accounts/{account_id}`
- `GET /admin/transactions?page=1&limit=10`
- `GET /admin/transactions/{transaction_id}`
- `DELETE /admin/transactions/{transaction_id}`

## Auth Flow
Login -> access token:
1. Client calls `POST /auth/login` with name/password.
2. Server verifies credentials.
3. Server returns JWT access token.

Use Bearer token:
```http
Authorization: Bearer <access_token>
```

401 vs 403:
- `401 Unauthorized` means missing/invalid token or invalid credentials.
- `403 Forbidden` means valid token but insufficient permission.

## Interview Narrative Preparation

System Architecture:
- Client -> FastAPI Router -> Service Layer -> PostgreSQL
- Auth and RBAC enforced via dependencies and role checks

Auth Flow:
- JWT generated on login
- Token validated on each protected route
- RBAC enforced with `require_role("admin")`

Ownership Model:
- Users can only access or mutate their own accounts and transactions
- Admin can access and delete across users

Failure Handling:
- Centralized exception handlers with consistent error response shape
- No raw tracebacks in responses
- Structured logging for key actions and failures

Performance Thinking:
- Pagination for list routes
- Connection pooling via `psycopg2.pool.SimpleConnectionPool`
- Redis cache for admin list/detail routes with explicit invalidation

## Deployment Link
Live URL: `TBD`
