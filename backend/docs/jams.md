# JAMs — Documentación de la App

## ¿Qué es una JAM?

Una **JAM** es el espacio colaborativo de un viaje (`Trip`). Cada Trip tiene como máximo una JAM (relación `OneToOneField`). La JAM no duplica la información del viaje; se encarga de gestionar **quién** participa, con **qué rol** y qué **permisos** tiene cada participante.

La app `jams` actúa como **hub de autorización colaborativa** para el resto de los módulos de MOVE. Futuros módulos como `itinerary`, `expenses` y `votes` deben importar los helpers de permisos de `apps.jams.services` en lugar de implementar su propia lógica de membresía.

---

## Modelos

### `Jam`

| Campo        | Tipo                  | Descripción                                    |
|--------------|-----------------------|------------------------------------------------|
| `id`         | `BigAutoField` (PK)   | Identificador único                            |
| `trip`       | `OneToOneField(Trip)` | El viaje al que pertenece. Un trip → un JAM.   |
| `name`       | `CharField(255)`      | Nombre del JAM (requerido)                     |
| `description`| `TextField`           | Descripción opcional                           |
| `created_by` | `ForeignKey(User)`    | Usuario que creó el JAM (no editable vía API)  |
| `is_active`  | `BooleanField`        | `True` por defecto                             |
| `created_at` | `DateTimeField`       | Auto-asignado                                  |
| `updated_at` | `DateTimeField`       | Auto-actualizado                               |

**Regla crítica:** Al crear un JAM, el sistema automáticamente agrega a `created_by` como `JamMember` con `role=admin` y `status=active` (via señal `post_save`).

---

### `JamMember`

| Campo       | Tipo               | Valores posibles                  |
|-------------|--------------------|-----------------------------------|
| `id`        | `BigAutoField`     | PK                                |
| `jam`       | `ForeignKey(Jam)`  | JAM al que pertenece              |
| `user`      | `ForeignKey(User)` | Usuario miembro                   |
| `role`      | `CharField`        | `admin` \| `member`               |
| `status`    | `CharField`        | `invited` \| `active` \| `removed`|
| `joined_at` | `DateTimeField`    | Auto-asignado al crear            |
| `created_at`| `DateTimeField`    | Auto-asignado                     |
| `updated_at`| `DateTimeField`    | Auto-actualizado                  |

**Constraint de unicidad:** `unique_together = ("jam", "user")`. No se pueden duplicar miembros.

---

## Servicios y Helpers (`apps/jams/services.py`)

Este archivo es la **fuente única de verdad** para control de acceso en JAMs. Todos los módulos futuros deben importar desde aquí.

### Predicados de permisos

```python
from apps.jams.services import (
    is_jam_admin,
    is_jam_member,
    can_view_jam,
    can_manage_jam,
    can_manage_jam_members,
    get_user_jam_role,
    guard_last_admin_or_raise,
    user_has_trip_access,
)
```

| Función                              | Retorna      | Descripción                                                       |
|--------------------------------------|--------------|-------------------------------------------------------------------|
| `get_user_jam_role(user, jam)`       | `str \| None` | Rol del usuario activo en la JAM (`'admin'`, `'member'`, `None`) |
| `is_jam_admin(user, jam)`            | `bool`       | `True` si es admin activo                                         |
| `is_jam_member(user, jam)`           | `bool`       | `True` si tiene membresía activa (admin o member)                 |
| `can_view_jam(user, jam)`            | `bool`       | `True` si puede ver la JAM (membresía activa)                     |
| `can_manage_jam(user, jam)`          | `bool`       | `True` si puede editar/archivar/eliminar el JAM (admin)           |
| `can_manage_jam_members(user, jam)`  | `bool`       | `True` si puede agregar/cambiar/remover miembros (admin)          |
| `user_has_trip_access(user, trip)`   | `bool`       | `True` si es organizador o participante del Trip                  |
| `guard_last_admin_or_raise(jam, membership, *, new_role, removing)` | `None` / `raises ValidationError` | Protege la invariante: siempre debe existir al menos un admin activo |

### Uso en módulos futuros

```python
# En apps/expenses/views.py (ejemplo)
from apps.jams.services import is_jam_member, is_jam_admin

def create_expense(request, jam_id):
    jam = get_object_or_404(Jam, pk=jam_id)

    if not is_jam_member(request.user, jam):
        raise PermissionDenied("Debes ser miembro de esta JAM para registrar gastos.")

    # Solo admins pueden aprobar gastos
    if expense.requires_approval and not is_jam_admin(request.user, jam):
        raise PermissionDenied("Solo admins pueden aprobar gastos.")
```

---

## Endpoints

Todos los endpoints requieren autenticación vía JWT cookie HTTP-Only (`move_access_token`).

### JAM anidada en Trip

| Método | URL                           | Descripción                              | Permisos mínimos         |
|--------|-------------------------------|------------------------------------------|--------------------------|
| `POST` | `/api/trips/{trip_id}/jam/`   | Crear la JAM única del viaje             | Autenticado + acceso al Trip |
| `GET`  | `/api/trips/{trip_id}/jam/`   | Obtener la JAM del viaje                 | Miembro activo de la JAM |

### JAM standalone

| Método   | URL                  | Descripción           | Permisos mínimos |
|----------|----------------------|-----------------------|------------------|
| `GET`    | `/api/jams/{jam_id}/` | Ver detalle de la JAM | Miembro activo   |
| `PATCH`  | `/api/jams/{jam_id}/` | Editar nombre/desc    | Admin activo     |
| `DELETE` | `/api/jams/{jam_id}/` | Eliminar la JAM       | Admin activo     |

### Miembros

| Método   | URL                                        | Descripción                    | Permisos mínimos |
|----------|--------------------------------------------|--------------------------------|------------------|
| `GET`    | `/api/jams/{jam_id}/members/`              | Listar miembros                | Miembro activo   |
| `POST`   | `/api/jams/{jam_id}/members/`              | Agregar miembro                | Admin activo     |
| `PATCH`  | `/api/jams/{jam_id}/members/{member_id}/`  | Cambiar rol o status           | Admin activo     |
| `DELETE` | `/api/jams/{jam_id}/members/{member_id}/`  | Remover miembro                | Admin activo     |

---

## Matriz de Permisos

| Acción                    | No autenticado | Autenticado (fuera de JAM) | Member activo | Admin activo |
|---------------------------|:--------------:|:--------------------------:|:-------------:|:------------:|
| Ver JAM                   | 401            | 403                        | ✅            | ✅           |
| Editar JAM                | 401            | 403                        | 403           | ✅           |
| Eliminar JAM              | 401            | 403                        | 403           | ✅           |
| Listar miembros           | 401            | 403                        | ✅            | ✅           |
| Agregar miembro           | 401            | 403                        | 403           | ✅           |
| Cambiar rol de miembro    | 401            | 403                        | 403           | ✅           |
| Remover miembro           | 401            | 403                        | 403           | ✅           |
| Crear JAM (vía Trip)      | 401            | 403 (sin acceso al Trip)   | ✅            | ✅           |

---

## Reglas de Negocio Críticas

1. **Un Trip → máximo un JAM.** La relación `OneToOneField` lo garantiza a nivel de base de datos.
2. **Sin miembros duplicados.** `unique_together = ("jam", "user")` lo garantiza a nivel de BD.
3. **El creador es siempre el primer admin.** La señal `post_save` en `Jam` crea automáticamente el `JamMember` con `role=admin, status=active`.
4. **`created_by` nunca se acepta del request body.** Se asigna forzosamente desde `request.user` en la vista.
5. **Siempre debe existir al menos un admin activo.** `guard_last_admin_or_raise()` en `services.py` lo hace cumplir. Se llama tanto en `PATCH` (degradación) como en `DELETE` (eliminación).

---

## Serializers

| Serializer                  | Uso                                         |
|-----------------------------|---------------------------------------------|
| `JamDetailSerializer`       | Respuestas GET (lectura enriquecida)         |
| `JamCreateUpdateSerializer` | POST y PATCH de Jam (escritura)             |
| `JamMemberSerializer`       | Respuestas de membresías (lectura)           |
| `JamMemberCreateSerializer` | POST de nuevo miembro                       |
| `JamMemberUpdateSerializer` | PATCH de rol/status de membresía            |

El campo `user` en respuestas solo expone: `id`, `username`, `first_name`, `last_name`, `avatar`. **Nunca expone email ni password.**

---

## Ejemplos de Request / Response

### Crear un JAM

```http
POST /api/trips/7/jam/
Content-Type: application/json
Cookie: move_access_token=<jwt>

{
  "name": "Viaje a Lisboa",
  "description": "JAM principal del viaje"
}
```

**Response 201:**
```json
{
  "id": 1,
  "trip_id": 7,
  "name": "Viaje a Lisboa",
  "description": "JAM principal del viaje",
  "is_active": true,
  "created_by": {
    "id": 3,
    "username": "alice",
    "first_name": "Alice",
    "last_name": "",
    "avatar": ""
  },
  "created_at": "2026-05-17T21:00:00Z",
  "updated_at": "2026-05-17T21:00:00Z"
}
```

### Agregar un miembro

```http
POST /api/jams/1/members/
Content-Type: application/json
Cookie: move_access_token=<jwt_admin>

{
  "user_id": 5,
  "role": "member"
}
```

**Response 201:**
```json
{
  "id": 2,
  "user": {
    "id": 5,
    "username": "bob",
    "first_name": "Bob",
    "last_name": "",
    "avatar": ""
  },
  "role": "member",
  "status": "active",
  "joined_at": "2026-05-17T21:05:00Z"
}
```

### Error: último admin

```http
DELETE /api/jams/1/members/1/
Cookie: move_access_token=<jwt_admin>
```

**Response 400:**
```json
[
  "Cannot remove the last active admin. Assign another admin first."
]
```

---

## Guía de Integración para Módulos Futuros

Al implementar `itinerary`, `expenses`, `votes` o `catalog`, sigue este patrón:

```python
# apps/itinerary/views.py
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.jams.models import Jam
from apps.jams.services import can_view_jam, is_jam_admin


class ActivityListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, jam_id):
        jam = get_object_or_404(Jam, pk=jam_id)

        # Delegar validación de membresía a jams.services
        if not can_view_jam(request.user, jam):
            raise PermissionDenied("No eres miembro de esta JAM.")

        # ... lógica de itinerary
```

**Regla:** Nunca consultes `JamMember` directamente desde otro módulo. Siempre usa las funciones de `apps.jams.services`.

---

## Tests

Los tests viven en `apps/jams/tests.py` y cubren **44 casos** organizados en:

| Clase                   | Qué prueba                                      |
|-------------------------|-------------------------------------------------|
| `ServiceTests`          | Helpers de permisos (`is_jam_admin`, etc.)      |
| `JamCreateTests`        | Creación, unicidad, permisos, anti-spoof        |
| `TripJamGetTests`       | GET via endpoint de trip                        |
| `JamDetailTests`        | GET/PATCH/DELETE con roles                      |
| `JamMemberListTests`    | Listar miembros                                 |
| `JamMemberAddTests`     | Agregar miembros, duplicados, acceso al trip    |
| `JamMemberUpdateTests`  | Cambiar rol, guardia del último admin           |
| `JamMemberRemoveTests`  | Remover miembros, guardia del último admin      |

Ejecutar solo los tests de JAMs:

```bash
docker compose exec backend python manage.py test apps.jams --verbosity=2
```
