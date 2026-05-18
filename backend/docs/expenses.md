# Expenses — Documentación de la App

## ¿Qué hace esta app?

La app `expenses` permite registrar y dividir gastos dentro de una **JAM** de MOVE.  
Cada gasto queda asociado a la JAM, registra quién pagó, cómo se divide el costo y el estado de pago de cada participante.

> **No implementa pagos reales.** `mark-paid` y `mark-pending` son tracking manual — no hay integración con Stripe, SPEI ni wallets.

La app depende de `apps.jams.services` para validar permisos de membresía. Nunca consulta `JamMember` directamente.

---

## Modelos

### `Expense`

| Campo        | Tipo                    | Descripción                                          |
|--------------|-------------------------|------------------------------------------------------|
| `id`         | `BigAutoField`          | PK                                                   |
| `jam`        | `ForeignKey(Jam)`       | JAM a la que pertenece el gasto                      |
| `title`      | `CharField(255)`        | Etiqueta corta, e.g. "Cena en el centro"             |
| `description`| `TextField`             | Detalle opcional                                     |
| `amount`     | `Decimal(10,2)`         | Total del gasto. Debe ser > 0 (CheckConstraint)      |
| `currency`   | `CharField(3)`          | Moneda, default `"MXN"`                              |
| `split_type` | `CharField`             | `equal` \| `custom`                                  |
| `category`   | `CharField`             | `food` \| `lodging` \| `transport` \| `activity` \| `nightlife` \| `shopping` \| `other` |
| `paid_by`    | `ForeignKey(User)`      | Quién adelantó el dinero                             |
| `created_by` | `ForeignKey(User)`      | Quién registró el gasto (siempre `request.user`)     |
| `is_active`  | `BooleanField`          | `False` = soft-deleted, excluido de listas y summary |
| `created_at` | `DateTimeField`         | Auto                                                 |
| `updated_at` | `DateTimeField`         | Auto                                                 |

### `ExpenseSplit`

| Campo         | Tipo               | Descripción                                          |
|---------------|--------------------|------------------------------------------------------|
| `id`          | `BigAutoField`     | PK                                                   |
| `expense`     | `ForeignKey`       | Gasto al que pertenece                               |
| `user`        | `ForeignKey(User)` | Participante                                         |
| `amount_owed` | `Decimal(10,2)`    | Monto que este usuario debe (≥ 0)                    |
| `status`      | `CharField`        | `pending` \| `paid`                                  |
| `paid_at`     | `DateTimeField?`   | Cuándo fue marcado como pagado (null = pendiente)    |

**Constraint:** `unique_together = ("expense", "user")` — un usuario no puede tener dos splits en el mismo gasto.

---

## Reglas de Negocio

1. **`created_by` siempre es `request.user`** — no se acepta del body.
2. **El split de `paid_by` se auto-marca como `paid`** al crear el gasto; los demás quedan `pending`.
3. **`DELETE` es soft delete** — cambia `is_active=False`. El registro persiste en la BD.
4. **Solo se pueden editar `title`, `description` y `category`** en PATCH. `amount`, `paid_by`, `split_type` y `splits` son inmutables.
5. **Para `custom`, la suma de `amount_owed` debe igualar `amount`** (tolerancia de ±0.01).
6. **Todos los participantes deben ser miembros activos de la JAM** al momento de crear el gasto.

---

## Endpoints

Todos requieren autenticación JWT HTTP-Only (`move_access_token`).

### Rutas bajo `/api/jams/`

| Método | URL | Descripción | Permiso mínimo |
|--------|-----|-------------|----------------|
| `GET`  | `/api/jams/{jam_id}/expenses/` | Listar expenses activos | Miembro activo |
| `POST` | `/api/jams/{jam_id}/expenses/` | Crear expense | Miembro activo |
| `GET`  | `/api/jams/{jam_id}/expenses/summary/` | Resumen financiero | Miembro activo |

### Rutas bajo `/api/expenses/`

| Método  | URL | Descripción | Permiso mínimo |
|---------|-----|-------------|----------------|
| `GET`   | `/api/expenses/{expense_id}/` | Detalle con splits | Miembro activo |
| `PATCH` | `/api/expenses/{expense_id}/` | Editar título/desc/categoría | Admin o creador |
| `DELETE`| `/api/expenses/{expense_id}/` | Soft delete | Admin o creador |
| `GET`   | `/api/expenses/{expense_id}/splits/` | Listar splits | Miembro activo |
| `PATCH` | `/api/expenses/{expense_id}/splits/{split_id}/mark-paid/` | Marcar split pagado | Dueño del split o admin |
| `PATCH` | `/api/expenses/{expense_id}/splits/{split_id}/mark-pending/` | Revertir a pendiente | Admin o creador del expense |

---

## Matriz de Permisos

| Acción | No autenticado | Outsider (sin JAM) | Member activo | Admin activo |
|---|:-:|:-:|:-:|:-:|
| Listar expenses | 401 | 403 | ✅ | ✅ |
| Crear expense | 401 | 403 | ✅ | ✅ |
| Ver detalle | 401 | 403 | ✅ | ✅ |
| Editar (PATCH) | 401 | 403 | 403 | ✅ |
| Eliminar (soft) | 401 | 403 | 403 | ✅ |
| Ver summary | 401 | 403 | ✅ | ✅ |
| Listar splits | 401 | 403 | ✅ | ✅ |
| mark-paid | 401 | 403 | ✅ (propio split) | ✅ |
| mark-pending | 401 | 403 | 403 | ✅ |

> El **creador del expense** (aunque sea `member`) también puede editar/eliminar y revertir splits.

---

## Serializers

| Serializer | Uso |
|---|---|
| `ExpenseUserSerializer` | User anidado sin datos sensibles (solo id, username, nombres) |
| `ExpenseSplitSerializer` | Lectura de splits con user nested |
| `ExpenseListSerializer` | Vista compacta para `GET /expenses/` |
| `ExpenseDetailSerializer` | Vista completa con splits embebidos |
| `ExpenseCreateSerializer` | POST — maneja `equal` y `custom` |
| `ExpenseUpdateSerializer` | PATCH — solo `title`, `description`, `category` |

---

## Servicios (`apps/expenses/services.py`)

### Helpers de permisos

```python
from apps.expenses.services import (
    can_view_expense,
    can_manage_expense,
    can_mark_split_paid,
    can_mark_split_pending,
)
```

| Función | Retorna | Descripción |
|---|---|---|
| `can_view_expense(user, expense)` | `bool` | Miembro activo de la JAM |
| `can_manage_expense(user, expense)` | `bool` | Admin de JAM o creador del expense |
| `can_mark_split_paid(user, split)` | `bool` | Dueño del split o admin |
| `can_mark_split_pending(user, split)` | `bool` | Admin o creador del expense |

### Funciones de creación

```python
from apps.expenses.services import create_equal_expense, create_custom_expense

# Equal split
expense = create_equal_expense(jam, {
    "title": "Cena",
    "amount": Decimal("300.00"),
    "currency": "MXN",
    "category": "food",
    "paid_by": user_a,
    "participant_ids": [user_a.pk, user_b.pk, user_c.pk],
}, created_by=request.user)

# Custom split
expense = create_custom_expense(jam, {
    "title": "Hotel",
    "amount": Decimal("1000.00"),
    "currency": "MXN",
    "category": "lodging",
    "paid_by": user_a,
    "splits": [
        {"user_id": user_a.pk, "amount_owed": Decimal("600.00")},
        {"user_id": user_b.pk, "amount_owed": Decimal("400.00")},
    ],
}, created_by=request.user)
```

### Summary

```python
from apps.expenses.services import calculate_jam_expense_summary

summary = calculate_jam_expense_summary(jam)
# {
#   "total_expenses": Decimal("1300.00"),
#   "total_paid":    Decimal("600.00"),
#   "total_pending": Decimal("700.00"),
#   "balances": {
#     "alice": {"paid": 1300.00, "owes": 600.00, "net_balance": 700.00},
#     "bob":   {"paid": 0.00,    "owes": 400.00, "net_balance": -400.00},
#   },
#   "pending_splits": [
#     {"expense_id": 1, "expense_title": "Hotel", "username": "bob", "amount_owed": 400.00}
#   ]
# }
```

---

## Ejemplos de Request / Response

### Crear expense igual

```http
POST /api/jams/3/expenses/
Content-Type: application/json
Cookie: move_access_token=<jwt>

{
  "title": "Cena grupal",
  "amount": "300.00",
  "currency": "MXN",
  "split_type": "equal",
  "category": "food",
  "participant_ids": [1, 2, 3]
}
```

**Response 201:**
```json
{
  "id": 7,
  "jam": 3,
  "title": "Cena grupal",
  "amount": "300.00",
  "currency": "MXN",
  "split_type": "equal",
  "category": "food",
  "paid_by": {"id": 1, "username": "alice", "first_name": "Alice", "last_name": ""},
  "created_by": {"id": 1, "username": "alice", "first_name": "Alice", "last_name": ""},
  "is_active": true,
  "splits": [
    {"id": 10, "user": {"username": "alice"}, "amount_owed": "100.00", "status": "paid",    "paid_at": "2026-05-17T21:00:00Z"},
    {"id": 11, "user": {"username": "bob"},   "amount_owed": "100.00", "status": "pending", "paid_at": null},
    {"id": 12, "user": {"username": "carol"}, "amount_owed": "100.00", "status": "pending", "paid_at": null}
  ]
}
```

### Crear expense custom

```http
POST /api/jams/3/expenses/
Content-Type: application/json
Cookie: move_access_token=<jwt>

{
  "title": "Hotel",
  "amount": "1000.00",
  "split_type": "custom",
  "category": "lodging",
  "splits": [
    {"user_id": 1, "amount_owed": "600.00"},
    {"user_id": 2, "amount_owed": "400.00"}
  ]
}
```

### Marcar split como pagado

```http
PATCH /api/expenses/7/splits/11/mark-paid/
Cookie: move_access_token=<jwt_bob>
```

**Response 200:**
```json
{"id": 11, "user": {"username": "bob"}, "amount_owed": "100.00", "status": "paid", "paid_at": "2026-05-18T10:30:00Z"}
```

### Summary de la JAM

```http
GET /api/jams/3/expenses/summary/
Cookie: move_access_token=<jwt>
```

**Response 200:**
```json
{
  "total_expenses": "300.00",
  "total_paid": "200.00",
  "total_pending": "100.00",
  "balances": {
    "alice": {"paid": "300.00", "owes": "100.00", "net_balance": "200.00"},
    "bob":   {"paid": "0.00",   "owes": "100.00", "net_balance": "-100.00"},
    "carol": {"paid": "0.00",   "owes": "100.00", "net_balance": "-100.00"}
  },
  "pending_splits": [
    {"expense_id": 7, "expense_title": "Cena grupal", "username": "carol", "amount_owed": "100.00"}
  ]
}
```

---

## Tests

```bash
# Solo expenses (62 tests)
docker compose exec backend python manage.py test apps.expenses --verbosity=2

# Suite completa (168 tests)
docker compose exec backend python manage.py test --verbosity=1
```

### Cobertura

| Clase de test | Qué prueba |
|---|---|
| `CalculateEqualSplitsTests` | Matemática de split igual, redondeo, casos borde |
| `ServicePermissionTests` | `can_view`, `can_manage`, `can_mark_*` con admin/member/outsider |
| `CreateEqualExpenseTests` | Creación, auto-paid del `paid_by`, rechazo de outsiders |
| `CreateCustomExpenseTests` | Montos correctos, error si suma != amount |
| `SummaryTests` | Totales, soft-delete excluido, net_balance, pending_splits |
| `MarkSplitTests` | Transiciones `pending → paid → pending` |
| `ExpenseListCreateAPITests` | GET/POST permisos, soft-delete en lista, `created_by` inmune |
| `ExpenseSummaryAPITests` | Summary vía API, outsider 403, soft-delete excluido |
| `ExpenseDetailAPITests` | GET/PATCH/DELETE permisos, `amount` inmutable |
| `SplitAPITests` | Listar, mark-paid, mark-pending, doble mark = 400 |
| `ExpenseIntegrationCookieTests` | Flujo completo con JWT HTTP-Only cookies reales |

---

## Notas de Migración

Las migraciones `0001_initial.py` y `0002_initial.py` originales fueron eliminadas y reemplazadas por una nueva `0001_initial.py` limpia.

**Si ya aplicaste las migraciones viejas en local, ejecuta:**

```bash
# Opción 1 — Resetear solo expenses
docker compose exec backend python manage.py migrate expenses zero
docker compose exec backend python manage.py migrate expenses

# Opción 2 — Borrar y recrear la DB SQLite completa
rm backend/db.sqlite3
docker compose exec backend python manage.py migrate
```

No hay datos de producción en riesgo (la app estaba en stub). En staging/producción siempre coordinar con el equipo antes de resetear migraciones.
