# MOVE

> Organiza viajes en grupo, divide gastos y descubre destinos con inteligencia de datos.

---

## Stack Tecnológico

| Capa       | Tecnología                              |
|------------|------------------------------------------|
| Backend    | Python 3.11, Django 4.2, DRF, Gunicorn  |
| Frontend   | Vite, React 18, Material UI              |
| Base datos | SQLite (dev) → PostgreSQL (prod)         |
| Data       | JSON / CSV + pandas                      |
| Infra      | Docker, AWS ECS Fargate, Terraform       |

---

## Estructura del Repositorio

```
move/
├── backend/           → API REST (Django + DRF)
│   ├── apps/
│   │   ├── authentication/
│   │   ├── users/
│   │   ├── trips/
│   │   ├── jams/
│   │   ├── expenses/
│   │   └── search_engine/
│   ├── config/        → Proyecto Django (settings, urls, wsgi)
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── requirements.txt
│
├── frontend/          → SPA Vite + React (no modificar desde aquí)
│
├── data/
│   ├── raw/           → Datasets originales
│   └── processed/     → Datos listos para consumir
│
├── docs/
│   ├── arquitectura.md
│   ├── decisiones.md
│   └── figma-link.txt
│
└── infra/             → Terraform (pendiente)
```

---

## Cómo correr el Backend

### Opción A — Local (virtualenv)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

API disponible en: `http://localhost:8000/api/`  
Health check: `http://localhost:8000/api/health/`

### Opción B — Docker (solo backend)

```bash
cd backend
docker build -t move-backend .
docker run -p 8000:8000 --env-file .env move-backend
```

### Opción C — Docker Compose (stack completo) ⭐

```bash
# 1. Crear el archivo de variables de entorno del backend
cp backend/.env.example backend/.env

# 2. Levantar todo el stack
docker compose up --build
```

| Servicio  | URL                            |
|-----------|--------------------------------|
| Frontend  | http://localhost               |
| Backend   | http://localhost:8000/api/     |
| Health    | http://localhost:8000/api/health/ |

```bash
# Detener
docker compose down

# Ver logs en tiempo real
docker compose logs -f
```

---

## Endpoints base

| Método | URL                       | Descripción           |
|--------|---------------------------|-----------------------|
| GET    | `/api/health/`            | Health check          |
| CRUD   | `/api/users/`             | Usuarios              |
| CRUD   | `/api/trips/`             | Viajes                |
| CRUD   | `/api/jams/`              | JAMs (grupos)         |
| CRUD   | `/api/expenses/`          | Gastos                |
| CRUD   | `/api/search/destinations/` | Motor de búsqueda   |

---

## Contribuir

1. Crea una rama desde `main`: `git checkout -b feature/nombre`
2. Haz tus cambios
3. Abre un Pull Request describiendo el cambio

Ver `docs/arquitectura.md` y `docs/decisiones.md` para contexto técnico.
