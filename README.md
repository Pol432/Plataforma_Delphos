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

### 0. Atajo: todo de una vez

```bash
./dev.sh            # backend (Docker) + frontend (Vite), espera a que respondan
./dev.sh stop       # detiene ambos
./dev.sh status     # estado de los tres servicios
./dev.sh logs web   # logs de la API (o db | front)
```

Instala `node_modules` la primera vez si falta. Docker por sí solo no basta:
`docker compose` cubre PostgreSQL y la API, pero el frontend corre fuera.
Las secciones siguientes explican cada pieza por separado.

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

*Sobre `.venv`:* es local y está en `.gitignore` — no se versiona, así que
nunca hay que "arreglarlo" en el repo: se borra y se rehace. Un venv deja de
funcionar si el Python del sistema se actualiza por debajo (típico en Arch):
`bin/python` pasa a apuntar al intérprete nuevo mientras los paquetes siguen
en `lib/python3.X/site-packages` de la versión vieja, y entonces *nada* es
importable aunque los binarios estén ahí (`pytest` existe pero falta
`_pytest`). Se reconoce comparando `pyvenv.cfg` con
`.venv/bin/python --version`. Solución: `rm -rf .venv` y rehacerlo.

Si no tienes un Python <=3.11 a mano, MindSpore no se puede instalar y el
motor no corre en local — para eso está el contenedor. Aun así puedes correr
la mayor parte de los tests, que son numpy puro y se saltan solos los que
piden el framework:

```bash
cd oracle/recommendation
python3 -m venv .venv && .venv/bin/pip install pytest numpy pandas scikit-learn
.venv/bin/python -m pytest tests/ -q      # 47 passed, 9 skipped
```

`setup_env.sh` **no** sirve para esto: es el script del contenedor (escribe
symlinks en `/usr/bin` y da por hecho `/workspace`), no crea ningún venv.

**`skill_graph`** — grafo temporal. Requiere una base PostgreSQL propia
(`DATABASE_URL` en un `.env`) y aplicar `db/migrations/*.sql`. Ver
`oracle/README.md`.

## Estado conocido

Puntos verificados en un arranque limpio, útiles para no perder tiempo:

- ~~**`/health` devuelve 404.**~~ **Resuelto (2026-08-06).** La ruta no existía:
  `main.py` sólo declaraba `/`. Añadida como sonda de *liveness* — responde 200
  mientras el proceso atienda peticiones y no consulta la base de datos. El
  `HEALTHCHECK` del `Dockerfile` ya pasa por ahí.
- **Conflicto de nombres de contenedor.** El `docker-compose.yml` fija
  `container_name: aurum_postgres` / `aurum_api`. Si tienes otro proyecto con
  esos mismos nombres, el arranque falla con *"container name already in use"*.
  Solución sin borrar nada: `docker compose -p delphos up -d` junto con un
  override que renombre los contenedores.
- ~~**Tests del backend: ~149 fallan por imports faltantes en `app/db/base.py`.**~~
  **Resuelto (2026-08-06).** El diagnóstico era incorrecto: no falta ningún
  import. Los 18 modelos comparten un único `Base` y `app/models/__init__.py`
  los importa todos. El síntoma real es que la suite no llega ni a colectarse si
  no hay una base de datos accesible, porque `app/main.py` ejecuta
  `create_all()` contra el engine real en tiempo de import.

  **Estado actual: 408 passed, 19 skipped, 0 failed**, verificado tanto contra
  SQLite como contra el PostgreSQL del compose. La suite usa SQLite por defecto;
  para validarla contra Postgres real:

      docker compose exec \
        -e TEST_DATABASE_URL=postgresql://postgres:postgres@db:5432/aurum_test \
        web pytest

  Conviene hacerlo antes de cerrar cualquier hito: SQLite oculta fallos reales.
  Al habilitarlo aparecieron 2 tests que sólo pasaban por artefactos suyos
  (comparación de datetimes naive contra columnas `timezone=True`, y un id de
  usuario fijo que asumía que las secuencias vuelven atrás con el rollback —
  en PostgreSQL no lo hacen). Ambos corregidos.
- **`skill_graph` no corre end-to-end:** `checkpoints/task_eval_model.ckpt` no
  existe en el repo ni en su historial. El código no falla — cae a **pesos
  aleatorios**, así que sus predicciones no significan nada hasta que aparezca
  el checkpoint. Ver `oracle/skill_graph/README_CHECKPOINT_STATUS.md`.
- **Métricas de `recommendation` no reproducidas:** el checkpoint carga y hace
  inferencia, pero el AUC 0.7763 de `evaluation_results.json` no se puede
  reconfirmar porque el MindRecord de test no está versionado. Ver
  `oracle/recommendation/README_CHECKPOINT_STATUS.md`.
- **Los números de `/api/v1/oracle/recommend` no son del modelo.** Aunque la
  respuesta diga `"engine": "wide_and_deep"`, el Wide&Deep sólo decide el
  ORDEN de la lista. Todos los valores visibles —`engagement_probability`,
  `skill_overlap_score`, `difficulty_match_score` y `confidence_interval`— los
  calcula el heurístico `heuristic_bridge_v1`, porque la calibración del modelo
  está sin resolver y su probabilidad cruda no se publica. Al demostrar el
  endpoint, no atribuir esos números al modelo entrenado.
  `confidence_interval`, además, no estima incertidumbre: es una banda fija de
  +/-0.1 alrededor del score heurístico.

## Notas

- Los checkpoints (`*.ckpt`) **sí** se versionan por ahora — son pequeños.
- `node_modules/` y `.venv/` no se copiaron ni se versionan: reinstalar con
  `npm install` (frontend) y `pip install -r requirements.txt` (backend/oracle).
