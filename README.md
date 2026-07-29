# Plataforma Delphos

Monorepo de la Plataforma Delphos. Cuatro áreas de trabajo, cada una con su dueño
y su rama.

## Estructura

```
backend/                 API y autenticación (FastAPI, Alembic, Docker)
frontend/                Cliente web (Vite + React/TS)
oracle/
  learning_path/         Optimizador de rutas de aprendizaje
  recommendation/        Wide & Deep para recomendación de carreras (MindSpore)
  skill_graph/           Grafo temporal de habilidades
```

## Dueños y ramas

| Carpeta     | Dueño  | Rama               |
|-------------|--------|--------------------|
| `backend/`  | Matías | `feature/backend`  |
| `frontend/` | Alex   | `feature/frontend` |
| `oracle/`   | Paúl   | `feature/oracle`   |

Cada quien trabaja en su rama sobre su carpeta; ver `oracle/README.md` para el
detalle de los tres subsistemas de IA (hoy independientes, no fusionados).

## Quickstart

Requisitos: **Docker** (con Compose), **Node 20+** y **Python 3.10+**.
Backend y frontend son independientes — puedes levantar solo uno.

### 1. Backend (API + PostgreSQL)

```bash
cd backend
docker compose up -d --build db web
```

Levanta PostgreSQL 15 y la API en `http://localhost:8000`.

| Endpoint | Descripción |
|---|---|
| `http://localhost:8000/` | Estado del servicio |
| `http://localhost:8000/docs` | Swagger UI (35 endpoints) |

Las tablas se crean solas al arrancar (SQLAlchemy `create_all`), así que **no
hace falta correr Alembic** para el arranque en desarrollo.

Comprobación rápida (registro → login → ruta protegida):

```bash
curl -X POST http://localhost:8000/api/v1/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"demo","email":"demo@test.dev","full_name":"Demo","password":"Demo12345!"}'

TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/token \
  -d 'username=demo&password=Demo12345!' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

curl http://localhost:8000/api/v1/users/me -H "Authorization: Bearer $TOKEN"
```

Otros comandos: `docker compose logs -f web`, `docker compose down`
(añade `-v` para borrar también los datos).

### 2. Frontend (Vite + React)

```bash
cd frontend
npm install
npm run dev
```

Queda en `http://localhost:5173`. La URL de la API se configura con
`VITE_API_URL` en `frontend/.env` (por defecto `http://localhost:8000`); el
backend ya acepta CORS desde el puerto 5173, así que ambos funcionan juntos sin
tocar nada. Para compilar producción: `npm run build`.

> `yarn install` / `yarn dev` también funcionan, pero el lockfile versionado es
> `package-lock.json`: si usas yarn, no commitees el `yarn.lock` que genera.

### 3. Oracle (subsistemas de IA)

Los tres son independientes entre sí y del backend; cada uno tiene su propio
`requirements.txt`. Usa un entorno virtual por subsistema.

**`learning_path`** — optimizador de rutas. No necesita base de datos ni GPU:

```bash
cd oracle/learning_path
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Paso obligatorio: genera data/skill_graph_v1.json (no está versionado).
# Sin esto, los tests y el demo fallan con FileNotFoundError.
python -m learning_path.core.build_initial_graph

python -m pytest tests/ -q     # 61 tests
python scripts/demo.py         # demo end-to-end
```

**`recommendation`** — Wide & Deep con MindSpore. Requiere **Python 3.10**
(MindSpore 2.6.0 no publica wheels para 3.12+):

```bash
cd oracle/recommendation
python3.10 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Si PyPI no sirve MindSpore para tu plataforma, usa el índice de Huawei que
indica `requirements.txt`. El checkpoint entrenado
(`checkpoints/dao_wide_deep_final.ckpt`) está versionado y carga sin errores;
la arquitectura se reconstruye con los valores de
`checkpoints/training_config.json`. Ver `README.md` de la carpeta para el
detalle de notebooks y datos.

**`skill_graph`** — grafo temporal. Requiere una base PostgreSQL propia
(`DATABASE_URL` en un `.env`) y aplicar `db/migrations/*.sql`. Ver
`oracle/README.md`.

## Estado conocido

Puntos verificados en un arranque limpio, útiles para no perder tiempo:

- **`/health` devuelve 404.** El `HEALTHCHECK` del `Dockerfile` apunta ahí pero
  la ruta no existe; el contenedor puede aparecer como *unhealthy* aunque la API
  funcione. Usa `/` para comprobar que está viva.
- **Conflicto de nombres de contenedor.** El `docker-compose.yml` fija
  `container_name: aurum_postgres` / `aurum_api`. Si tienes otro proyecto con
  esos mismos nombres, el arranque falla con *"container name already in use"*.
  Solución sin borrar nada: `docker compose -p delphos up -d` junto con un
  override que renombre los contenedores.
- **Tests del backend:** 271 pasan, pero ~149 fallan porque `app/db/base.py` no
  importa todos los modelos, así que `Base.metadata.create_all` no crea tablas
  como `empresas` o `content_categories` en la SQLite de test (*no such table*).
  Es un fallo del arnés de tests, no de la aplicación.
- **`skill_graph` no corre end-to-end:** `checkpoints/task_eval_model.ckpt` no
  existe en el repo ni en su historial. El código no falla — cae a **pesos
  aleatorios**, así que sus predicciones no significan nada hasta que aparezca
  el checkpoint. Ver `oracle/skill_graph/README_CHECKPOINT_STATUS.md`.
- **Métricas de `recommendation` no reproducidas:** el checkpoint carga y hace
  inferencia, pero el AUC 0.7763 de `evaluation_results.json` no se puede
  reconfirmar porque el MindRecord de test no está versionado. Ver
  `oracle/recommendation/README_CHECKPOINT_STATUS.md`.

## Notas

- Los checkpoints (`*.ckpt`) **sí** se versionan por ahora — son pequeños.
- `node_modules/` y `.venv/` no se copiaron ni se versionan: reinstalar con
  `npm install` (frontend) y `pip install -r requirements.txt` (backend/oracle).
