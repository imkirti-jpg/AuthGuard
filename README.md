# AuthGuard - Production-Grade Authentication Service

A robust, production-ready authentication and authorization service built with **FastAPI**, **PostgreSQL**, and **Redis**. AuthGuard provides stateless JWT-based authentication, role-based access control (RBAC), refresh tokens, and advanced security features like account locking and password reset.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Database Migrations](#database-migrations)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## Features

### Authentication
- ✅ **User Registration** - Duplicate email checking and secure password hashing with bcrypt
- ✅ **User Login** - OAuth2-compliant authentication with email/password
- ✅ **JWT Access Tokens** - Stateless authentication tokens with configurable expiration
- ✅ **Refresh Tokens** - Long-lived tokens stored in Redis for session management
- ✅ **Logout** - Token revocation and session termination
- ✅ **Account Locking** - Automatic account lock after failed login attempts with configurable threshold
- ✅ **Password Reset** - Reset tokens stored in Redis with expiration

### Authorization
- ✅ **Role-Based Access Control (RBAC)** - Admin and user roles
- ✅ **Default Roles** - Pre-configured `admin` and `user` roles assigned at registration
- ✅ **Admin Role Assignment** - Endpoint to promote users to admin
- ✅ **Protected Routes** - Role-based access control for endpoints

### Security
- ✅ **Bcrypt Password Hashing** - Industry-standard password security with salt
- ✅ **JWT Token Verification** - Cryptographic token validation with HS256
- ✅ **Account Lockout** - Brute-force protection with configurable failed attempt threshold
- ✅ **Redis Session Storage** - Revocable refresh and reset tokens
- ✅ **Async Architecture** - Non-blocking database operations

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.100+ |
| **Web Server** | Uvicorn |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0+ (Async) |
| **Migrations** | Alembic |
| **Authentication** | JWT (python-jose), OAuth2 |
| **Password Hashing** | Passlib + Bcrypt |
| **Session Store** | Redis |
| **Testing** | pytest, httpx |
| **Validation** | Pydantic v2 |
| **Python** | 3.10+ |

## Project Structure

```
AuthGuard/
├── alembic.ini                 # Alembic configuration
├── pytest.ini                  # pytest configuration
├── plan.md                     # Project roadmap
├── .env                        # Environment variables (create as needed)
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   │
│   ├── api/
│   │   ├── dependency.py       # Dependency injection (JWT, roles)
│   │   ├── v1.py               # API versioning (reserved)
│   │   └── routes/
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── users.py        # User profile endpoints
│   │       ├── admin.py        # Admin management endpoints
│   │       └── refresh_route.py # Token refresh endpoints
│   │
│   ├── core/
│   │   ├── config.py           # Settings and environment configuration
│   │   ├── security.py         # Password hashing and JWT utilities
│   │   ├── refresh.py          # Refresh token management
│   │   ├── pass_reset.py       # Password reset utilities
│   │   └── seed_roles.py       # Role seeding script
│   │
│   ├── db/
│   │   ├── base.py             # SQLAlchemy declarative base
│   │   ├── base_class.py       # Base model class
│   │   ├── session.py          # Database session management
│   │   └── redis.py            # Redis client configuration
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── role.py             # Role model
│   │   ├── refresh_tokens.py   # Refresh token model
│   │   └── user_roles.py       # User-Role association
│   │
│   ├── schemas/
│   │   ├── user.py             # User request/response schemas
│   │   └── refresh.py          # Refresh token schemas
│   │
│   └── services/
│       ├── auth_service.py     # Business logic for authentication
│       └── exceptions.py       # Custom exceptions
│
├── migrations/
│   ├── env.py                  # Alembic environment configuration
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration scripts
│
├── tests/
│   ├── conftest.py             # pytest configuration and fixtures
│   ├── test_auth.py            # Authentication tests
│   └── test_routes.py          # Route and integration tests
│
└── README.md                   # This file
```

## Prerequisites

- **Python 3.10+**
- **PostgreSQL 12+**
- **Redis 6+**
- **Docker & Docker Compose** (optional, for containerization)
- **pip** or **poetry** (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AuthGuard
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv .venv

# Activate virtual environment
# On Windows
.\.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install fastapi uvicorn sqlalchemy psycopg[binary] alembic pydantic-settings passlib bcrypt python-jose redis pytest httpx
```

### 4. Set Up Environment Variables

```bash
# Create .env file with required settings
touch .env

# Edit .env with your settings (see example below)
```

### Example .env Configuration

```env
# Database Configuration
DB_USERNAME=authuser
DB_PASSWORD=your_secure_password
DB_HOSTNAME=localhost
DB_PORT=5432
DB_NAME=authguard_db
DATABASE_URL=postgresql+asyncpg://authuser:your_secure_password@localhost:5432/authguard_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
RESET_TOKEN_EXPIRE_MINUTES=30

# Security Configuration
MAX_FAILED_LOGIN_ATTEMPTS=5
LOCKOUT_MINUTES=15

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### 6. Set Up Databases

#### PostgreSQL

```bash
# Using Docker (recommended)
docker run -d \
  --name authguard-db \
  -e POSTGRES_USER=authuser \
  -e POSTGRES_PASSWORD=your_secure_password \
  -e POSTGRES_DB=authguard_db \
  -p 5432:5432 \
  postgres:15

# Or create manually if you have PostgreSQL installed
createdb -U postgres authguard_db
```

#### Redis

```bash
# Using Docker (recommended)
docker run -d \
  --name authguard-redis \
  -p 6379:6379 \
  redis:7-alpine

# Or install and run locally on macOS/Linux
redis-server
```

### 7. Run Database Migrations

```bash
# Apply migrations
alembic upgrade head

# Seed default roles (creates admin and user roles)
python -c "from app.core.seed_roles import seed_roles; import asyncio; asyncio.run(seed_roles())"
```

## Configuration

### Environment Variables Reference

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `DB_USERNAME` | string | PostgreSQL user | `authuser` |
| `DB_PASSWORD` | string | PostgreSQL password | `securepass123` |
| `DB_HOSTNAME` | string | PostgreSQL host | `localhost` |
| `DB_PORT` | integer | PostgreSQL port | `5432` |
| `DB_NAME` | string | Database name | `authguard_db` |
| `DATABASE_URL` | string | Full connection string | `postgresql+asyncpg://...` |
| `SECRET_KEY` | string | JWT signing key (32+ chars) | `your-secret-key` |
| `ALGORITHM` | string | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | integer | Refresh token TTL | `7` |
| `RESET_TOKEN_EXPIRE_MINUTES` | integer | Password reset token TTL | `30` |
| `MAX_FAILED_LOGIN_ATTEMPTS` | integer | Login attempts before lock | `5` |
| `LOCKOUT_MINUTES` | integer | Account lockout duration | `15` |
| `REDIS_URL` | string | Redis connection URL | `redis://localhost:6379/0` |

## Running the Application

### Development Mode

```bash
# Start the development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
# Run without auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

### Base URL
```
http://localhost:8000
```

**Error Responses:**
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - User does not have admin role
- `404 Not Found` - User not found
- `500 Internal Server Error` - Admin role not initialized

---

### Authentication Flow Diagram

```
1. Registration:
   POST /auth/register → User Created → Default "user" role assigned

2. Login:
   POST /auth/login → JWT Access Token + Refresh Token (Redis)

3. Protected Access:
   GET /auth/users/me + Bearer Token → User Data

4. Token Refresh:
   POST /auth/refresh + Refresh Token → New Access Token

5. Logout:
   POST /auth/logout + Refresh Token → Token Revoked

6. Password Reset:
   POST /auth/forgot-password → Reset Token (Redis)
   POST /auth/reset-password + Reset Token → Password Updated
```

## Testing

### Run All Tests

```bash
# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run with logging
pytest -v -s
```

### Test Structure

- **tests/conftest.py** - Shared fixtures and test configuration
- **tests/test_auth.py** - Authentication endpoint tests
- **tests/test_routes.py** - Route and integration tests

### Sample Test Output

```
tests/test_auth.py::test_register_user PASSED                     [20%]
tests/test_auth.py::test_login_user PASSED                        [40%]
tests/test_auth.py::test_invalid_credentials PASSED               [60%]
tests/test_routes.py::test_get_current_user PASSED                [80%]
tests/test_routes.py::test_unauthorized_access PASSED             [100%]

====== 5 passed in 2.34s ======
```

## Database Migrations

### Creating Migrations

```bash
# Auto-generate migration based on model changes
alembic revision --autogenerate -m "Descriptive message"

# Create empty migration for manual changes
alembic revision -m "Custom migration"
```

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +2

# Revert to previous migration
alembic downgrade -1

# Show current migration status
alembic current

# Show migration history
alembic history
```


## Architecture

### Design Patterns

1. **Separation of Concerns**
   - Routes: HTTP layer
   - Services: Business logic
   - Models: Data models
   - Schemas: Request/response validation

2. **Dependency Injection**
   - Database sessions
   - Current user identification
   - Role-based access control

3. **Async Architecture**
   - Non-blocking database operations
   - Efficient resource utilization
   - Better scalability

### Security Features

1. **Password Security**
   - Bcrypt hashing with salt
   - Configurable round counts
   - Secure comparison

2. **Token Management**
   - JWT access tokens with expiration
   - Opaque refresh tokens stored in Redis
   - Token revocation capabilities

3. **Account Protection**
   - Failed login attempt tracking
   - Automatic account locking
   - Configurable lockout duration

4. **Role-Based Access Control**
   - Granular permission management
   - Admin and user roles
   - Extensible role system

### Data Flow

```
Client Request
    ↓
FastAPI Router
    ↓
Dependency Injection (Auth, DB)
    ↓
Service Layer (Business Logic)
    ↓
SQLAlchemy ORM
    ↓
PostgreSQL Database
    ↓
Response
```
## Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -U authuser -d authguard_db -h localhost

# Check if migrations are applied
alembic current
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli ping

# Check refresh tokens in Redis
redis-cli KEYS "user:*"
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (if needed)
kill -9 <PID>
```

### Token Verification Failures

1. Check `SECRET_KEY` matches between token creation and verification
2. Verify token hasn't expired
3. Ensure `ALGORITHM` is set correctly (default: `HS256`)

## Future Enhancements

- [ ] Email verification on registration
- [ ] Two-factor authentication (2FA)
- [ ] OAuth2 social login (Google, GitHub)
- [ ] Email notifications for password reset
- [ ] Audit logging for security events
- [ ] Custom permission system beyond roles

## License

This project is licensed under the MIT License - see the LICENSE file for details.

