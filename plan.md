# Project Roadmap: Auth Service Foundation

This roadmap focuses on building a production-grade Authentication and Authorization service using FastAPI, PostgreSQL, and Redis.

## WEEK 1: FOUNDATION (Infrastructure & Basic Auth)

### Day 1: Repo & Infrastructure
*Goal: A running application with clean architecture.*
- [ ] **Initialize Repo:** Create directory `auth-service` and run `git init`.
- [ ] **Folder Structure:** Create `app/` (api, core, db, models, schemas).
- [ ] **Environment:** Setup python venv, install `fastapi`, `uvicorn`, `pydantic-settings`.
- [ ] **Config:** Create `.env` and `app/core/config.py` (load DB URL, Secret Key).
- [ ] **Health Check:** Create `app/main.py` with `GET /health`.
- [ ] **Commit:** `git add . && git commit -m "Initial commit"`
- [ ] **Deliverable:** Run `uvicorn app.main:app --reload` and see `{ "status": "ok" }`.

### Day 2: Database & Models
*Goal: The ability to persist data.*
- [ ] **Docker:** Spin up local PostgreSQL container.
- [ ] **SQLAlchemy:** Configure `app/db/session.py` (engine) and `app/db/base.py`.
- [ ] **Models:** Create `app/models/` classes:
    - [ ] `User`
    - [ ] `Role`
    - [ ] `Permission`
    - [ ] Association tables (`UserRole`, `RolePermission`)
- [ ] **Alembic:** Run `alembic init alembic` and configure `env.py`.
- [ ] **Migration:** Run `alembic revision --autogenerate` -> `alembic upgrade head`.
- [ ] **Deliverable:** Verify tables exist in the database.

### Day 3: Password Security
*Goal: Storing users safely.*
- [ ] **Libs:** Install `passlib[bcrypt]`.
- [ ] **Hashing Utility:** Create `app/core/security.py` (`get_password_hash`, `verify_password`).
- [ ] **Schemas:** Create Pydantic models for `UserCreate` and `UserLogin`.
- [ ] **Register API:** `POST /auth/register` (Check email -> Hash PWD -> Save DB).
- [ ] **Login Stub:** `POST /auth/login` (Verify credentials only).
- [ ] **Deliverable:** Register a user and see the hashed password in DB.

### Day 4: JWT Access Tokens
*Goal: Stateless authentication.*
- [ ] **Libs:** Install `python-jose` or `pyjwt`.
- [ ] **Token Logic:** Add `create_access_token` to `security.py`.
- [ ] **Login Update:** Return JWT on successful login.
- [ ] **Dependency:** Create `get_current_user` (verify JWT signature).
- [ ] **Protect Route:** Create `GET /users/me` requiring the dependency.
- [ ] **Deliverable:** Access `/users/me` via Swagger UI using the Authorize button.

### Day 5: Refresh Tokens + Redis
*Goal: Long-lived sessions with revocation capability.*
- [ ] **Redis:** Spin up Redis container; install `redis` python client.
- [ ] **Refresh Logic:** Generate opaque token; store in Redis (`key: user_id, val: token, ttl: 7days`).
- [ ] **Login Update:** Return `{ access_token, refresh_token }`.
- [ ] **Refresh API:** `POST /auth/refresh` (Validate refresh token -> Issue new Access Token).
- [ ] **Deliverable:** Use a refresh token to get a new access token without logging in again.

### Day 6: Logout + Revocation
*Goal: Session termination.*
- [ ] **Logout API:** `POST /auth/logout`.
- [ ] **Revocation:** Delete the specific refresh token from Redis.
- [ ] **Test:** Ensure the deleted refresh token can no longer generate access tokens.
- [ ] **Deliverable:** A secure logout flow.

### Day 7: Cleanup + Tests
*Goal: Reliability and tech debt payment.*
- [ ] **Refactor:** Ensure business logic is in `services/`, not `routers/`.
- [ ] **Testing:** Install `pytest`, `httpx`.
- [ ] **Unit Tests:** Write tests for Register, Login, and Protected Routes.
- [ ] **Linting:** Run `ruff` or `black` to standardize code.
- [ ] **Deliverable:** Green test suite.

---

## WEEK 2: AUTHORIZATION (RBAC & Security)

### Day 8: Roles & Permissions
*Goal: Granular access control.*
- [ ] **Seeding:** Create script to insert default roles (`admin`, `user`).
- [ ] **Role Checker:** Create dependency `RoleChecker(allowed_roles=["admin"])`.
- [ ] **Enforce:** Apply `@Depends(RoleChecker)` to specific routes.
- [ ] **Deliverable:** A standard user gets a 403 when hitting an admin route.

### Days 9-10: Admin APIs
*Goal: User management.*
- [ ] **Role Assignment:** `POST /admin/users/{id}/role`.
- [ ] **Logic:** Update `UserRole` table.
- [ ] **Deliverable:** An admin can promote a standard user to admin.

### Day 11: Rate Limiting
*Goal: Brute-force protection.*
- [ ] **Middleware:** intercept `POST /login` requests.
- [ ] **Redis:** Track failed attempts by IP/Email.
- [ ] **Lockout:** Block requests after 5 failed attempts for X minutes.
- [ ] **Deliverable:** Spamming wrong passwords results in a 429 error.

### Day 13: Password Reset Flow
*Goal: Account recovery.*
- [ ] **Forgot API:** `POST /auth/forgot-password` (Generate token -> Redis).
- [ ] **Reset API:** `POST /auth/reset-password` (Verify token -> Update Hash).
- [ ] **Deliverable:** Ability to reset password without being logged in.

### Day 14: Final Security Review
*Goal: Production readiness.*
- [ ] **Audit:** Check token TTLs (Time To Live).
- [ ] **Logs:** Ensure no PII/Secrets in logs.
- [ ] **CORS:** strict origin policies.
- [ ] **Deliverable:** Ready for deployment.