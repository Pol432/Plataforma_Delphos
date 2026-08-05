# TODO Matías — `role` y `country` en el registro

## Qué pasa

La pantalla de registro (`frontend/src/screens/Screen1Register.jsx:284`) manda tres
campos que el backend no tiene declarados: `role`, `country` y `birth_year`.

Hasta ahora Pydantic los descartaba en silencio y la API devolvía `201`, así que
parecía que se guardaban. No se guardaba ninguno.

## Qué se ha hecho ya (parche, sin tocar la base de datos)

- `UserCreate` lleva `extra="forbid"`: un campo inesperado ahora da **422** en vez
  de fingir que se guardó.
- `birth_year` se convierte a `birth_date`, que **ya existe** como columna. El año
  se normaliza al **1 de enero** (no viene mes ni día); es una convención, no un
  dato real del usuario. Si te vale otra cosa, cámbiala.
- `role` y `country` **no se han tocado**: hacen falta columnas nuevas y eso es
  decisión tuya.

**Efecto inmediato:** con el frontend tal y como está hoy, el registro devuelve
422 nombrando `role` y `country`. Antes devolvía 201 y perdía los datos. Hay que
arreglar una de las dos puntas (o el modelo, o el payload del frontend).

## Lo que haría falta por tu parte

### 1. Decidir el tipo de cada campo

- **`role`** — ¿enum cerrado (`student` / `teacher` / `admin`…) o texto libre?
  ¿Un usuario puede tener más de uno? Ahora mismo el frontend manda `"student"`.
  Ojo: si el rol determina permisos, esto **no** puede venir del registro sin
  validar, o cualquiera se registra como `admin`.
- **`country`** — ¿texto libre, ISO-3166 (`EC`), o FK a una tabla de países?
  Ya existen `regions` / `provinces` / `cities` (`app/models/catalog.py:16-77`) y
  `users.city_id` apunta a `cities`, así que el país quizá deba deducirse de ahí
  en vez de guardarse suelto y arriesgar que se contradigan.

### 2. Migración de Alembic

Una revisión nueva que añada las columnas a `users`, en el estilo del resto:

```
alembic revision -m "add role and country to users"
alembic upgrade head
```

Con `op.add_column(...)` para cada campo. Puntos a tener en cuenta:

- **Nullable o con default.** Ya hay filas en `users`, así que `nullable=False`
  sin `server_default` peta la migración. O las creas nullable, o les pones un
  default y luego lo quitas.
- **`downgrade()`** con los `op.drop_column(...)` correspondientes.
- Si `role` acaba siendo un enum de verdad, hay que crear el tipo en la migración
  (y borrarlo en el downgrade); es el punto donde se suele romper.
- Si `country` acaba siendo FK, necesita su tabla y su índice.

### 3. Tocar también

- `app/models/user.py` — las columnas nuevas.
- `app/schemas/user.py` — declararlas en `UserCreate` (y en `UserOut` si deben
  devolverse). Con `extra="forbid"` puesto, mientras no estén declaradas el
  registro del frontend seguirá dando 422.
- `app/services/user_service.py:35` — hace `User(**user_data.model_dump())`, así
  que en cuanto los campos existan en el modelo se persisten solos.

## Cómo comprobarlo

```bash
curl -X POST http://localhost:8000/api/v1/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"x@example.com","password":"SecurePass123!","full_name":"X",
       "username":"x","role":"student","country":"Ecuador","birth_year":2000}'
```

- **Hoy:** `422`, nombrando `role` y `country`.
- **Cuando esté hecho:** `201` y los tres campos de vuelta en la respuesta.

Estado actual verificado: `birth_year: 2000` → `birth_date: "2000-01-01"` (201),
y `birth_year: 1850` → 422 por rango.
