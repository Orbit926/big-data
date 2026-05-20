# Arquitectura — MOVE

## Visión General

MOVE es un monorepo con cuatro capas principales:

```
move/
├── backend/       → API REST (Django + DRF)
├── frontend/      → SPA (Vite 8 + React 19 + Tailwind CSS)
├── data/          → Datasets para el motor de búsqueda
└── infra/         → Infraestructura como código (Terraform → pendiente)
```

---

## Backend

- **Framework**: Django 4.2 + Django REST Framework
- **Base de datos**: SQLite (desarrollo) → PostgreSQL (producción en AWS RDS)
- **Servidor**: Gunicorn detrás de un ALB en AWS ECS (Fargate)
- **Autenticación**: JWT HTTP-Only cookies (`JWTCookieAuthentication`)

### Apps

| App             | Responsabilidad                                                  |
|-----------------|------------------------------------------------------------------|
| `users`         | Gestión de usuarios y perfiles                                   |
| `authentication`| Login, logout, registro, refresh de tokens JWT                   |
| `trips`         | Viajes y su ciclo de vida (organizer + participants)             |
| `jams`          | Espacio colaborativo del viaje: miembros, roles y permisos       |
| `expenses`      | División de gastos compartidos por JAM (implementado)             |
| `search_engine` | Motor de búsqueda de destinos con Big Data                       |

---

## JAMs — Espacio Colaborativo

Cada `Trip` puede tener **como máximo un JAM** (relación `OneToOneField`).

### Roles
| Rol    | Permisos                                                                 |
|--------|--------------------------------------------------------------------------|
| admin  | Ver, editar, archivar/eliminar JAM, listar, agregar, cambiar y remover miembros |
| member | Ver JAM y listar miembros. Sin capacidad de modificar nada.              |

### Servicios reutilizables (`apps/jams/services.py`)
Módulos futuros (`itinerary`, `votes`, `expenses`, `catalog`) deben importar
estas funciones para validar permisos sin duplicar lógica:

- `is_jam_admin(user, jam)` → bool
- `is_jam_member(user, jam)` → bool
- `can_view_jam(user, jam)` → bool
- `can_manage_jam(user, jam)` → bool
- `can_manage_jam_members(user, jam)` → bool
- `get_user_jam_role(user, jam)` → str | None

### Endpoints JAM

```
POST   /api/trips/{trip_id}/jam/                     Crear JAM del viaje
GET    /api/trips/{trip_id}/jam/                     Obtener JAM del viaje
GET    /api/jams/{jam_id}/                           Detalle de JAM
PATCH  /api/jams/{jam_id}/                           Editar JAM (admin)
DELETE /api/jams/{jam_id}/                           Eliminar JAM (admin)
GET    /api/jams/{jam_id}/members/                   Listar miembros (member+)
POST   /api/jams/{jam_id}/members/                   Agregar miembro (admin)
PATCH  /api/jams/{jam_id}/members/{member_id}/      Cambiar rol/status (admin)
DELETE /api/jams/{jam_id}/members/{member_id}/      Remover miembro (admin)
```

---

## Frontend

- **Framework**: Vite 8 + React 19
- **UI**: Tailwind CSS (vía CDN) + CSS personalizado
- **Estado**: Context API / State de React
- **Comunicación**: API `fetch` nativa → `/api/`

---

## Data

- Datasets en formato JSON/CSV almacenados en `data/raw/`
- Procesados con scripts Python en `data/processed/`
- Consumidos por la app `search_engine` del backend

---

## Infraestructura (pendiente)

- AWS ECS Fargate para el contenedor del backend
- AWS RDS PostgreSQL como base de datos
- AWS S3 para archivos estáticos
- Terraform en `/infra` (no tocar hasta definir staging)
