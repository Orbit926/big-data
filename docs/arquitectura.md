# Arquitectura — MOVE

## Visión General

MOVE es un monorepo con cuatro capas principales:

```
move/
├── backend/       → API REST (Django + DRF)
├── frontend/      → SPA (Vite + React + MUI)
├── data/          → Datasets para el motor de búsqueda
└── infra/         → Infraestructura como código (Terraform → pendiente)
```

---

## Backend

- **Framework**: Django 4.2 + Django REST Framework
- **Base de datos**: SQLite (desarrollo) → PostgreSQL (producción en AWS RDS)
- **Servidor**: Gunicorn detrás de un ALB en AWS ECS (Fargate)
- **Autenticación**: Token / JWT (por implementar)

### Apps

| App             | Responsabilidad                              |
|-----------------|----------------------------------------------|
| `users`         | Gestión de usuarios y perfiles               |
| `trips`         | Viajes y su ciclo de vida                    |
| `jams`          | Grupos dentro de un viaje                    |
| `expenses`      | División de gastos por JAM                   |
| `search_engine` | Motor de búsqueda de destinos con Big Data   |

---

## Frontend

- **Framework**: Vite + React 18
- **UI**: Material UI (MUI)
- **Estado**: Context API / Zustand (por definir)
- **Comunicación**: Axios → `http://localhost:8000/api/`

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
