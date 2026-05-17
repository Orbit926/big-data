# Register — Documentación de Feature

> **App:** `apps.authentication` (flujo) + `apps.users` (modelo) | **Stack:** Django REST Framework + JWT HTTP-only Cookies

---

## Tabla de contenidos

1. [Arquitectura: auth vs users](#1-arquitectura-auth-vs-users)
2. [Endpoint](#2-endpoint)
3. [Campos del request](#3-campos-del-request)
4. [Respuestas](#4-respuestas)
5. [Flujo completo de registro](#5-flujo-completo-de-registro)
6. [Integración con JWT-Auth](#6-integración-con-jwt-auth)
7. [Guía para el frontend](#7-guía-para-el-frontend)
8. [Guía de uso rápido (ejemplos cURL)](#8-guía-de-uso-rápido-ejemplos-curl)
9. [Tests](#9-tests)

---

## 1. Arquitectura: auth vs users

Este proyecto mantiene una separación limpia de responsabilidades:

| App | Responsabilidad |
|-----|----------------|
| `apps.users` | **Define qué es un usuario** — modelo `User`, perfil, avatar, bio |
| `apps.authentication` | **Define cómo accede** — register, login, logout, refresh, /me |

El endpoint de registro vive en `authentication` porque el flujo completo es:
**crear cuenta → emitir cookies JWT → usuario logueado en un solo paso.**

Internamente, `RegisterView` usa `get_user_model()` para crear el usuario — nunca importa `apps.users.User` directamente, manteniendo el desacoplamiento correcto.

```
POST /api/auth/register/
       │
       ├── RegisterSerializer.validate()   → valida campos, unicidad, passwords
       ├── RegisterSerializer.create()     → User.objects.create_user() vía get_user_model()
       ├── generate_access_token(user)     → JWT de acceso (15 min por defecto)
       ├── generate_refresh_token(user)    → JWT de refresco (7 días por defecto)
       └── set_auth_cookies(response)      → cookies HttpOnly en la respuesta
```

---

## 2. Endpoint

```
POST /api/auth/register/
```

- **Autenticación requerida:** No (`AllowAny`)
- **Método HTTP:** `POST`
- **Content-Type:** `application/json`

---

## 3. Campos del request

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `username` | `string` | ✅ | Nombre de usuario único (máx. 150 chars) |
| `email` | `string` | ✅ | Email único (normalizado a minúsculas) |
| `password` | `string` | ✅ | Contraseña (mín. 8 chars, validada por Django) |
| `password_confirm` | `string` | ✅ | Debe ser idéntica a `password` |
| `first_name` | `string` | ❌ | Nombre (máx. 150 chars) |
| `last_name` | `string` | ❌ | Apellido (máx. 150 chars) |

### Validaciones aplicadas

1. **Unicidad de `username`** — case-insensitive (`alice` y `Alice` son el mismo)
2. **Unicidad de `email`** — case-insensitive, normalizado a minúsculas al guardar
3. **Confirmación de contraseña** — `password` y `password_confirm` deben coincidir
4. **Django password validators** — longitud mínima, contraseñas comunes, similitud con el username

---

## 4. Respuestas

### `201 Created` — Registro exitoso

```json
{
  "detail": "Account created successfully.",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "bio": "",
    "avatar": "",
    "date_joined": "2026-05-17T20:00:00Z",
    "is_staff": false
  }
}
```

Junto con la respuesta se emiten **dos cookies HTTP-only**:

| Cookie | TTL | Descripción |
|--------|-----|-------------|
| `move_access_token` | 15 min (configurable) | JWT de acceso para peticiones autenticadas |
| `move_refresh_token` | 7 días (configurable) | JWT de refresco para obtener nuevos access tokens |

> [!IMPORTANT]
> El campo `password` **nunca** aparece en la respuesta. La contraseña se almacena hasheada con el algoritmo de Django (PBKDF2 + SHA256 por defecto).

### `400 Bad Request` — Errores de validación

```json
{
  "username": ["A user with that username already exists."],
  "email": ["A user with that email already exists."],
  "password_confirm": ["Passwords do not match."]
}
```

Los errores son por campo — el frontend puede mostrarlos inline en el formulario.

---

## 5. Flujo completo de registro

```
Cliente                    Backend
  │                           │
  │  POST /api/auth/register/ │
  │ ─────────────────────────►│
  │                           │  RegisterSerializer.validate()
  │                           │  ├─ username único?  → 400 si no
  │                           │  ├─ email único?     → 400 si no
  │                           │  └─ passwords match? → 400 si no
  │                           │
  │                           │  User.objects.create_user()
  │                           │  generate_access_token()
  │                           │  generate_refresh_token()
  │                           │  set_auth_cookies()
  │                           │
  │  ◄─────────────────────── │  201 Created
  │  Set-Cookie: move_access_token=...;  HttpOnly; SameSite=Lax
  │  Set-Cookie: move_refresh_token=...; HttpOnly; SameSite=Lax
  │                           │
  │  GET /api/auth/me/        │  ← usuario ya autenticado
  │ ─────────────────────────►│
  │  ◄─────────────────────── │  200 OK { username: "alice", ... }
```

---

## 6. Integración con JWT-Auth

Después del registro el usuario queda **inmediatamente autenticado** — no necesita hacer login por separado. Las cookies emitidas son idénticas a las de `/api/auth/login/`.

El flujo de refresco y logout es el mismo que para login:

```bash
# Refrescar access token cuando expire
POST /api/auth/refresh/

# Cerrar sesión (limpia ambas cookies)
POST /api/auth/logout/
```

Ver [`jwt_auth.md`](./jwt_auth.md) para la documentación completa del sistema JWT.

---

## 7. Guía para el frontend

### Configuración del cliente

```typescript
// credentials: 'include' es indispensable para que el browser envíe/reciba cookies
const res = await fetch('/api/auth/register/', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'alice',
    email: 'alice@example.com',
    password: 'StrongPass123!',
    password_confirm: 'StrongPass123!',
    first_name: 'Alice',   // opcional
    last_name: 'Smith',    // opcional
  }),
});
```

### Manejo de errores por campo

```typescript
if (res.status === 400) {
  const errors = await res.json();
  // errors es un objeto con los campos que fallaron:
  // { username: ["..."], email: ["..."], password_confirm: ["..."] }

  if (errors.username)         showError('username', errors.username[0]);
  if (errors.email)            showError('email', errors.email[0]);
  if (errors.password_confirm) showError('password_confirm', errors.password_confirm[0]);
}
```

### Después del registro exitoso

```typescript
if (res.status === 201) {
  const { user } = await res.json();
  // El usuario ya está logueado — las cookies se establecieron automáticamente.
  // Puedes guardar el objeto `user` en el estado de la app.
  setCurrentUser(user);
  navigate('/dashboard');
}
```

### Anti-patrones a evitar

- ❌ Enviar `password` en texto plano sin HTTPS en producción
- ❌ Almacenar el token JWT en `localStorage` — las cookies HTTP-only son la protección contra XSS
- ❌ Redirigir a `/login` después del registro — el usuario ya tiene sesión activa
- ❌ Mostrar un mensaje genérico en errores 400 — los errores son por campo, úsalos en el form

---

## 8. Guía de uso rápido (ejemplos cURL)

```bash
# Registro exitoso (guarda cookies en /tmp/cookies.txt)
curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -c /tmp/cookies.txt \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "StrongPass123!",
    "password_confirm": "StrongPass123!"
  }' | python3 -m json.tool

# Verificar que el auto-login funcionó (usar las cookies del registro)
curl -s http://localhost:8000/api/auth/me/ \
  -b /tmp/cookies.txt | python3 -m json.tool

# Error: username duplicado
curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"other@example.com","password":"StrongPass123!","password_confirm":"StrongPass123!"}' \
  | python3 -m json.tool

# Error: passwords no coinciden
curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","email":"bob@example.com","password":"StrongPass123!","password_confirm":"Wrong!"}' \
  | python3 -m json.tool
```

---

## 9. Tests

### Tests unitarios (sin Docker)

```bash
# Solo tests de registro
docker compose exec backend python manage.py test apps.authentication.tests.RegisterViewTests --verbosity=2

# Suite completa de auth
docker compose exec backend python manage.py test apps.authentication --verbosity=2

# Suite completa (auth + users + trips)
docker compose exec backend python manage.py test apps.authentication apps.users apps.trips --verbosity=2
```

### Cobertura de casos

| Test | Escenario | Resultado esperado |
|------|-----------|-------------------|
| `test_register_creates_user` | POST válido | `201`, usuario creado en DB |
| `test_register_returns_user_data` | POST válido | Body contiene `detail` + `user` con username correcto |
| `test_register_issues_access_cookie` | POST válido | Cookie `move_access_token` presente y `httponly=True` |
| `test_register_issues_refresh_cookie` | POST válido | Cookie `move_refresh_token` presente y `httponly=True` |
| `test_register_auto_login_me_accessible` | POST válido + GET /me/ | `/me/` retorna `200` con las cookies del registro |
| `test_register_with_optional_name_fields` | POST con `first_name`/`last_name` | Campos guardados correctamente en DB |
| `test_register_duplicate_username_returns_400` | Username ya existente | `400` con error en campo `username` |
| `test_register_duplicate_email_returns_400` | Email ya existente | `400` con error en campo `email` |
| `test_register_password_mismatch_returns_400` | Passwords no coinciden | `400` con error en campo `password_confirm` |
| `test_register_missing_email_returns_400` | Sin email | `400` |
| `test_register_missing_username_returns_400` | Sin username | `400` |
| `test_register_short_password_returns_400` | Password < 8 chars | `400` |

### Tests de integración (CI — Docker + curl)

El job `register-tests` en el workflow CI prueba los mismos escenarios contra el servidor real:

| Step | Qué prueba |
|------|-----------|
| R1 | Registro exitoso: `201`, body completo, sin leak de password |
| R2 | Auto-login: `/me/` accesible con las cookies del registro |
| R3 | `/me/` sin cookie → `401` |
| R4 | Username duplicado → `400` |
| R5 | Email duplicado → `400` |
| R6 | Passwords no coinciden → `400` |
| R7 | Password débil (muy corto) → `400` |
| R8 | Payload incompleto (sin email) → `400` |
| R9 | Campos opcionales (`first_name`, `last_name`) guardados en DB |
