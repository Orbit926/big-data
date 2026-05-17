# Trips — Documentación de Feature

> **App:** `apps.trips` | **Stack:** Django REST Framework + JWT HTTP-only Cookies

---

## Tabla de contenidos

1. [Modelo Trip](#1-modelo-trip)
2. [Permisos](#2-permisos)
3. [Endpoints](#3-endpoints)
4. [Integración con JWT-Auth](#4-integración-con-jwt-auth)
5. [Buenas prácticas para el frontend](#5-buenas-prácticas-para-el-frontend)
6. [Guía de uso rápido (ejemplos cURL)](#6-guía-de-uso-rápido-ejemplos-curl)
7. [Tests](#7-tests)

---

## 1. Modelo Trip

```python
# apps/trips/models.py
class Trip(models.Model):
    organizer    = ForeignKey(User, related_name="organized_trips")
    participants = ManyToManyField(User, related_name="participating_trips", blank=True)
    name         = CharField(max_length=255)
    description  = TextField(blank=True)
    start_date   = DateField(null=True, blank=True)
    end_date     = DateField(null=True, blank=True)
    created_at   = DateTimeField(auto_now_add=True)
    updated_at   = DateTimeField(auto_now=True)
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `BigAutoField` | PK auto-generada |
| `organizer` | FK → `User` | Usuario que crea y administra el viaje |
| `name` | `CharField(255)` | Nombre del viaje |
| `description` | `TextField` | Descripción opcional |
| `start_date` | `DateField` | Fecha de inicio (opcional) |
| `end_date` | `DateField` | Fecha de fin (opcional) |
| `participants` | M2M → `User` | Usuarios invitados al viaje |
| `created_at` | `DateTimeField` | Timestamp de creación (auto) |
| `updated_at` | `DateTimeField` | Timestamp de última modificación (auto) |

### Notas de diseño

- `organizer` **no** aparece en `participants` — son relaciones separadas, evitando duplicidad.
- La M2M `participants` se gestiona via `participant_ids` en el payload (lista de PKs).
- `__str__` devuelve `self.name`.

---

## 2. Permisos

Clase: `apps.trips.permissions.IsOrganizerOrReadOnly`

| Acción | Requisito |
|--------|-----------|
| `GET` (list, retrieve) | Usuario autenticado **AND** (organizador **OR** participante) |
| `POST` (create) | Cualquier usuario autenticado |
| `PUT` / `PATCH` (update) | Solo el **organizador** |
| `DELETE` (destroy) | Solo el **organizador** |

> [!IMPORTANT]
> El queryset ya está **scopeado** por usuario: un usuario ajeno al viaje recibirá `404 Not Found` en los endpoints de detalle, en lugar de `403`, para no revelar la existencia del recurso.

### Cadena de permisos en el ViewSet

```python
permission_classes = [IsAuthenticated, IsOrganizerOrReadOnly]
```

1. `IsAuthenticated` — rechaza peticiones sin cookie JWT válida (→ `401`).
2. `IsOrganizerOrReadOnly` — evalúa acceso a nivel de objeto (→ `403` si no es organizador).

---

## 3. Endpoints

Base URL: `/api/trips/`

### 3.1 `GET /api/trips/` — Listar viajes

Devuelve únicamente los viajes donde el usuario autenticado es **organizador** o **participante**.

**Request**

```http
GET /api/trips/
Cookie: move_access_token=<JWT>
```

**Response `200 OK`**

```json
[
  {
    "id": 1,
    "organizer": "alice",
    "name": "Summer Adventure",
    "description": "Road trip por la costa.",
    "start_date": "2026-07-01",
    "end_date": "2026-07-15",
    "participants": ["bob", "carol"],
    "created_at": "2026-05-17T10:00:00Z",
    "updated_at": "2026-05-17T10:00:00Z"
  }
]
```

---

### 3.2 `POST /api/trips/` — Crear viaje

El campo `organizer` se asigna automáticamente al usuario autenticado — **no** debe enviarse en el payload.

**Request**

```http
POST /api/trips/
Cookie: move_access_token=<JWT>
Content-Type: application/json

{
  "name": "Summer Adventure",
  "description": "Road trip por la costa.",
  "start_date": "2026-07-01",
  "end_date": "2026-07-15",
  "participant_ids": [2, 3]
}
```

**Response `201 Created`**

```json
{
  "id": 1,
  "organizer": "alice",
  "name": "Summer Adventure",
  "description": "Road trip por la costa.",
  "start_date": "2026-07-01",
  "end_date": "2026-07-15",
  "participants": ["bob", "carol"],
  "created_at": "2026-05-17T10:00:00Z",
  "updated_at": "2026-05-17T10:00:00Z"
}
```

**Errores comunes**

| Código | Causa |
|--------|-------|
| `401` | Sin cookie JWT o token expirado |
| `400` | Payload inválido (e.g. `name` vacío, `participant_ids` con PK inexistente) |

---

### 3.3 `GET /api/trips/<id>/` — Detalle de un viaje

**Request**

```http
GET /api/trips/1/
Cookie: move_access_token=<JWT>
```

**Responses**

| Código | Situación |
|--------|-----------|
| `200` | Organizador o participante autenticado |
| `401` | Sin autenticación |
| `404` | Viaje no existe o usuario ajeno al viaje |

---

### 3.4 `PUT /api/trips/<id>/` — Actualización completa

Solo el **organizador** puede actualizar. Todos los campos editables son requeridos en PUT.

**Request**

```http
PUT /api/trips/1/
Cookie: move_access_token=<JWT>
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Nueva descripción.",
  "start_date": "2026-08-01",
  "end_date": "2026-08-10",
  "participant_ids": [2]
}
```

**Responses**

| Código | Situación |
|--------|-----------|
| `200` | Actualización exitosa |
| `403` | Usuario autenticado no es el organizador |
| `404` | Viaje no existe o usuario ajeno |

---

### 3.5 `PATCH /api/trips/<id>/` — Actualización parcial

Igual que PUT pero solo se envían los campos a modificar.

```http
PATCH /api/trips/1/
Cookie: move_access_token=<JWT>
Content-Type: application/json

{
  "name": "Nuevo nombre"
}
```

---

### 3.6 `DELETE /api/trips/<id>/` — Eliminar viaje

Solo el **organizador** puede eliminar.

**Request**

```http
DELETE /api/trips/1/
Cookie: move_access_token=<JWT>
```

**Responses**

| Código | Situación |
|--------|-----------|
| `204 No Content` | Eliminación exitosa |
| `403` | No es el organizador |
| `404` | Viaje no existe o ajeno |

---

## 4. Integración con JWT-Auth

### Flujo completo

```
1. POST /api/auth/login/  →  cookies move_access_token + move_refresh_token set (HttpOnly)
2. GET  /api/trips/       →  browser envía cookies automáticamente
3. (token expira)
4. POST /api/auth/refresh/ →  nuevo access token en cookie
5. DELETE /api/auth/logout/ →  cookies borradas
```

### Autenticación en el backend

El backend usa `JWTCookieAuthentication` (configurado globalmente en `settings.py`):

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.authentication.backends.JWTCookieAuthentication",
    ],
}
```

Esto significa que **el frontend solo necesita configurar `credentials: 'include'`** y el navegador enviará las cookies automáticamente en cada petición.

### Headers de seguridad en producción

Las cookies tienen los atributos:

| Atributo | Valor prod | Propósito |
|----------|-----------|-----------|
| `HttpOnly` | ✅ | Bloquea acceso JS (previene XSS) |
| `Secure` | ✅ | Solo HTTPS |
| `SameSite` | `Lax` | Previene CSRF básico |

> [!NOTE]
> En desarrollo `JWT_COOKIE_SECURE=False` está permitido para funcionar con HTTP.

---

## 5. Buenas prácticas para el frontend

### Configuración del cliente HTTP (fetch / axios)

```typescript
// fetch
fetch('/api/trips/', {
  credentials: 'include',   // ← indispensable para enviar cookies
  headers: { 'Content-Type': 'application/json' },
});

// axios global
axios.defaults.withCredentials = true;
```

### Manejo de errores

```typescript
async function getTrips() {
  const res = await fetch('/api/trips/', { credentials: 'include' });

  if (res.status === 401) {
    // Token expirado → intentar refresh
    await refreshToken();
    return getTrips();
  }

  if (res.status === 403) {
    // No es el organizador — deshabilitar UI de edición
    showReadOnlyMode();
    return;
  }

  if (res.status === 404) {
    // Viaje no existe o no pertenece al usuario
    redirect('/trips');
    return;
  }

  return res.json();
}
```

### Determinar permisos en la UI

El campo `organizer` del response contiene el **username** del organizador. Compara con el usuario autenticado para mostrar/ocultar controles:

```typescript
const { data: trip } = await fetchTrip(id);
const { data: me } = await fetchCurrentUser();

const isOrganizer = trip.organizer === me.username;
// isOrganizer → mostrar botones Editar y Eliminar
```

### Crear/editar un viaje

```typescript
// Crear
await fetch('/api/trips/', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Mi Viaje',
    description: 'Descripción...',
    start_date: '2026-07-01',
    end_date: '2026-07-15',
    participant_ids: [2, 5],   // PKs de usuarios
  }),
});

// Edición parcial
await fetch(`/api/trips/${id}/`, {
  method: 'PATCH',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Nuevo nombre' }),
});
```

> [!TIP]
> Usa `PATCH` en lugar de `PUT` para actualizaciones parciales — envía solo los campos que cambiaron.

### Anti-patrones a evitar

- ❌ Enviar el `organizer` en el payload de creación — el backend lo ignora y lo asigna del token.
- ❌ Almacenar el JWT en `localStorage` — esto rompe la protección XSS.
- ❌ Asumir que un `403` en lista significa "sin acceso" — el queryset devuelve `404` para viajes ajenos.

---

## 6. Guía de uso rápido (ejemplos cURL)

```bash
# 1. Login (obtener cookie)
curl -c cookies.txt -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"StrongPass123!"}'

# 2. Crear viaje
curl -b cookies.txt -X POST http://localhost:8000/api/trips/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Cabo Trip","start_date":"2026-12-20","participant_ids":[2]}'

# 3. Listar viajes
curl -b cookies.txt http://localhost:8000/api/trips/

# 4. Detalle
curl -b cookies.txt http://localhost:8000/api/trips/1/

# 5. Edición parcial
curl -b cookies.txt -X PATCH http://localhost:8000/api/trips/1/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Cabo 2026"}'

# 6. Eliminar
curl -b cookies.txt -X DELETE http://localhost:8000/api/trips/1/
```

---

## 7. Tests

Ejecutar solo los tests de trips:

```bash
# Dentro del contenedor Docker
docker compose exec backend python manage.py test apps.trips --verbosity=2

# Fuera del contenedor (entorno local)
cd backend
python manage.py test apps.trips --verbosity=2
```

### Cobertura de casos

| Test | Escenario | Resultado esperado |
|------|-----------|-------------------|
| `TripCreateTests.test_create_trip_assigns_organizer` | POST autenticado | `201`, `organizer == username` |
| `TripCreateTests.test_create_trip_with_participants` | POST con `participant_ids` | Participantes asignados correctamente |
| `TripCreateTests.test_create_trip_unauthenticated_returns_401` | POST sin cookie | `401` |
| `TripListTests.test_user_sees_organized_and_participating_trips` | GET autenticado | Solo viajes propios/participados |
| `TripListTests.test_user_does_not_see_unrelated_trips` | GET autenticado | Viajes ajenos excluidos |
| `TripRetrieveTests.test_organizer_can_retrieve` | GET detail — organizador | `200` |
| `TripRetrieveTests.test_participant_can_retrieve` | GET detail — participante | `200` |
| `TripRetrieveTests.test_stranger_cannot_retrieve` | GET detail — ajeno | `404` |
| `TripUpdateTests.test_organizer_can_update` | PATCH — organizador | `200`, campo actualizado |
| `TripUpdateTests.test_participant_cannot_update_returns_403` | PATCH — participante | `403` |
| `TripDeleteTests.test_organizer_can_delete` | DELETE — organizador | `204`, registro eliminado |
| `TripDeleteTests.test_participant_cannot_delete_returns_403` | DELETE — participante | `403` |
