# JWT Auth — MOVE Backend

> **Stack**: Django 4.2 · Django REST Framework 3.15 · PyJWT 2.9
> **Cookie strategy**: HTTP-only cookies — tokens are never exposed to JavaScript.

---

## Table of Contents

1. [Architecture overview](#1-architecture-overview)
2. [Endpoint reference](#2-endpoint-reference)
3. [Token lifecycle](#3-token-lifecycle)
4. [Cookie security settings](#4-cookie-security-settings)
5. [Protecting your own endpoints](#5-protecting-your-own-endpoints)
6. [Frontend integration guide](#6-frontend-integration-guide)
7. [Error codes reference](#7-error-codes-reference)
8. [Environment variables](#8-environment-variables)
9. [Running tests locally](#9-running-tests-locally)

---

## 1. Architecture overview

```
Browser                          Django API
  │                                  │
  │  POST /api/auth/login/           │
  │  { login, password }  ──────────►│  Validate credentials
  │                                  │  Generate access JWT  (~15 min)
  │                                  │  Generate refresh JWT (~7 days)
  │◄── Set-Cookie: move_access_token  │  (both HTTP-only, SameSite=Lax)
  │◄── Set-Cookie: move_refresh_token │
  │                                  │
  │  GET /api/auth/me/               │
  │  (cookie sent automatically) ───►│  JWTCookieAuthentication reads cookie
  │◄── { id, username, email, ... }  │  validates access JWT → returns user
  │                                  │
  │  (access token expires)          │
  │  POST /api/auth/refresh/ ────────►│  Reads refresh cookie
  │◄── new Set-Cookie: access_token  │  Issues new access JWT
  │                                  │
  │  POST /api/auth/logout/ ─────────►│  Deletes both cookies
```

**Why HTTP-only cookies?**

- `httponly=True` → cookie is invisible to `document.cookie` → immune to XSS.
- `samesite=Lax` (dev) / `samesite=None; secure=True` (prod cross-site) → CSRF protection.
- The frontend **never sees** the raw token string. It only knows whether it is logged in by calling `/api/auth/me/`.

---

## 2. Endpoint reference

### `POST /api/auth/login/`

Authenticate and receive JWT cookies.

**Request body**

```json
{
  "login": "gabriel@example.com",   // email OR username
  "password": "supersecret"
}
```

**Success `200 OK`**

```json
{
  "detail": "Login successful.",
  "user": {
    "id": 1,
    "username": "gabriel",
    "email": "gabriel@example.com",
    "bio": "",
    "avatar": "",
    "date_joined": "2026-05-01T12:00:00Z",
    "is_staff": false
  }
}
```

Two cookies are set:

| Cookie name           | Type    | Max-Age |
|-----------------------|---------|---------|
| `move_access_token`   | access  | 15 min  |
| `move_refresh_token`  | refresh | 7 days  |

**Error `400 Bad Request`** — invalid credentials or disabled account.

---

### `POST /api/auth/logout/`

Clears both JWT cookies. Idempotent — safe to call even when not logged in.

**Success `200 OK`**

```json
{ "detail": "Logged out successfully." }
```

---

### `POST /api/auth/refresh/`

Exchange a valid refresh cookie for a new access token.

**Success `200 OK`** — new `move_access_token` cookie is set.

```json
{ "detail": "Token refreshed." }
```

**Error `401 Unauthorized`** — refresh cookie missing, expired, or invalid.

```json
{ "code": "refresh_expired", "detail": "Refresh token has expired. Please log in again." }
```

> ⚠️ On a `401` from `/refresh/`, **redirect the user to the login screen**. The refresh token cannot be recovered.

---

### `GET /api/auth/me/`

Returns the profile of the currently authenticated user.
Requires a valid `move_access_token` cookie.

**Success `200 OK`**

```json
{
  "id": 1,
  "username": "gabriel",
  "email": "gabriel@example.com",
  "bio": "Big data student",
  "avatar": "https://cdn.example.com/avatar.jpg",
  "date_joined": "2026-05-01T12:00:00Z",
  "is_staff": false
}
```

**Error `401 Unauthorized`** — no cookie, expired, or invalid token.

---

## 3. Token lifecycle

```
Login ──► [access: 15 min] ──► Expired ──► POST /refresh/ ──► [new access: 15 min]
                                                                        │
                            [refresh: 7 days] ──────────────────────────┘
                                    │
                             Expired/Invalid
                                    │
                            Redirect to /login
```

- Access tokens are **short-lived** (default 15 minutes).
- Refresh tokens live **7 days** and are only used once per rotation.
- The refresh token is **not rotated** on each use (server-side revocation is out of scope for now; add a `TokenBlocklist` model if needed).

---

## 4. Cookie security settings

| Setting          | Development     | Production (HTTPS)      |
|------------------|-----------------|-------------------------|
| `httponly`       | `True`          | `True`                  |
| `secure`         | `False`         | `True`                  |
| `samesite`       | `Lax`           | `None` (cross-site) or `Strict` |
| `path`           | `/`             | `/`                     |

Set these in `.env`:

```env
JWT_COOKIE_SECURE=True
JWT_COOKIE_SAMESITE=None
```

> If you use `SameSite=None`, `Secure=True` is **mandatory** (browser requirement).

---

## 5. Protecting your own endpoints

### Option A — Use `IsAuthenticated` permission (recommended)

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.authentication.backends import JWTCookieAuthentication

class MyProtectedView(APIView):
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": request.user.username})
```

### Option B — Global default (already configured in `settings.py`)

`JWTCookieAuthentication` is the default `DEFAULT_AUTHENTICATION_CLASSES`. Views that declare `permission_classes = [IsAuthenticated]` will automatically be protected without needing to set `authentication_classes`.

### Option C — Function-based views

```python
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.authentication.backends import JWTCookieAuthentication

@api_view(["GET"])
@authentication_classes([JWTCookieAuthentication])
@permission_classes([IsAuthenticated])
def my_view(request):
    return Response({"hello": request.user.username})
```

---

## 6. Frontend integration guide

### Basic fetch wrapper

```typescript
// lib/api.ts

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    credentials: "include",            // ← sends cookies cross-origin
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });
  return res;
}
```

> **`credentials: "include"`** is the single most important setting. Without it the browser will never send the HTTP-only cookies.

### Login

```typescript
async function login(login: string, password: string) {
  const res = await apiFetch("/api/auth/login/", {
    method: "POST",
    body: JSON.stringify({ login, password }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err?.detail ?? "Login failed");
  }

  return res.json(); // { detail, user }
}
```

### Logout

```typescript
async function logout() {
  await apiFetch("/api/auth/logout/", { method: "POST" });
  // Redirect to /login
}
```

### Automatic refresh with retry

```typescript
async function apiFetchWithRefresh(path: string, init: RequestInit = {}) {
  let res = await apiFetch(path, init);

  if (res.status === 401) {
    // Try refreshing the access token once
    const refreshRes = await apiFetch("/api/auth/refresh/", { method: "POST" });

    if (refreshRes.ok) {
      // Retry the original request — new access cookie is now set
      res = await apiFetch(path, init);
    } else {
      // Refresh failed → force logout
      await logout();
      throw new Error("Session expired. Please log in again.");
    }
  }

  return res;
}
```

### Checking auth state on app load

```typescript
async function getMe() {
  const res = await apiFetch("/api/auth/me/");
  if (res.status === 401) return null;          // not logged in
  return res.json();                            // User object
}

// In your root component / context provider:
const user = await getMe();
if (!user) router.push("/login");
```

### CSRF note

Django's `CsrfViewMiddleware` is active. For `POST`/`PUT`/`DELETE` requests from a different origin you must either:

1. **Disable CSRF for these views** (already done — auth views use `CSRFExemptSessionAuthentication` is NOT used; instead, add the origin to `CSRF_TRUSTED_ORIGINS` in `.env`).
2. Or fetch the CSRF token from the `csrftoken` cookie and include it as `X-CSRFToken` header.

> For cookie-based JWT auth, adding the frontend origin to `CSRF_TRUSTED_ORIGINS` in `.env` is the simplest approach and is already configured.

---

## 7. Error codes reference

All error responses follow this shape:

```json
{ "code": "machine_readable_code", "detail": "Human readable message." }
```

| Code                  | HTTP | Meaning                                          |
|-----------------------|------|--------------------------------------------------|
| `invalid_credentials` | 400  | Wrong email/username or password                 |
| `account_disabled`    | 400  | User is inactive                                 |
| `token_expired`       | 401  | Access token cookie is expired                   |
| `token_invalid`       | 401  | Access token is malformed or signature mismatch  |
| `token_type_error`    | 401  | Wrong token type (refresh used as access)        |
| `user_not_found`      | 401  | Token valid but user was deleted                 |
| `user_inactive`       | 401  | Token valid but account deactivated after issue  |
| `no_refresh_token`    | 401  | Refresh cookie missing on `/refresh/`            |
| `refresh_expired`     | 401  | Refresh token cookie has expired                 |
| `refresh_invalid`     | 401  | Refresh token malformed or tampered              |

---

## 8. Environment variables

All JWT variables are loaded from `backend/.env`. See `.env.example` for the full template.

| Variable                  | Default                   | Description                              |
|---------------------------|---------------------------|------------------------------------------|
| `JWT_ACCESS_MINUTES`      | `15`                      | Access token lifetime (minutes)          |
| `JWT_REFRESH_DAYS`        | `7`                       | Refresh token lifetime (days)            |
| `JWT_ACCESS_COOKIE_NAME`  | `move_access_token`       | Name of the access token cookie          |
| `JWT_REFRESH_COOKIE_NAME` | `move_refresh_token`      | Name of the refresh token cookie         |
| `JWT_COOKIE_SECURE`       | `False`                   | Set `True` on HTTPS (production)         |
| `JWT_COOKIE_SAMESITE`     | `Lax`                     | `Lax`, `Strict`, or `None` (cross-site)  |
| `CORS_ALLOWED_ORIGINS`    | (empty in dev)            | Comma-separated list of allowed origins  |
| `CSRF_TRUSTED_ORIGINS`    | `http://localhost:...`    | Comma-separated trusted origins for CSRF |

---

## 9. Running tests locally

```bash
# Inside the backend container or your virtual env
python manage.py test apps.authentication

# Or with pytest (if installed)
pytest apps/authentication/tests/ -v
```

The GitHub Actions CI workflow (`.github/workflows/jwt_auth_ci.yml`) runs the same suite on every push/PR touching `backend/`.
