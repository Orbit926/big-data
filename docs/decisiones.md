# Decisiones Técnicas — MOVE

## ADR-001: Monorepo

**Decisión**: Usar un monorepo para todo el proyecto.  
**Razón**: Equipo pequeño (4 personas), facilita compartir contratos de API y coordinar cambios cross-cutting sin gestionar múltiples repos.  
**Estado**: Aceptada

---

## ADR-002: Django + DRF para el backend

**Decisión**: Django con Django REST Framework.  
**Razón**: Batteries-included, ORM robusto, admin gratuito, gran ecosistema. DRF acelera la creación de APIs REST.  
**Estado**: Aceptada

---

## ADR-003: SQLite en desarrollo

**Decisión**: SQLite como base de datos en entorno local.  
**Razón**: Cero configuración para el equipo. La migración a PostgreSQL en producción es trivial con Django.  
**Estado**: Aceptada — revisar al llegar a staging

---

## ADR-004: Docker para el backend

**Decisión**: Dockerizar el backend con python:3.11-slim + gunicorn.  
**Razón**: Paridad entre entornos locales del equipo y futuro despliegue en AWS ECS Fargate.  
**Estado**: Aceptada

---

## ADR-005: Vite + React para el frontend

**Decisión**: Proyecto Vite ya inicializado, no se modifica desde backend.  
**Razón**: El equipo de frontend tiene autonomía total sobre su stack.  
**Estado**: Aceptada

---

## ADR-006: Big Data — Motor de búsqueda

**Decisión**: Datasets JSON/CSV en `data/`, procesados con Python, servidos vía API en `search_engine`.  
**Razón**: Enfoque académico que permite integrar técnicas de Big Data (pandas, análisis de clusters) sin infraestructura compleja en el MVP.  
**Estado**: Por implementar
