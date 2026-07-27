# Plataforma Delphos

Monorepo containing the Delphos platform: a React (Vite) frontend and a FastAPI + PostgreSQL backend (Delphos API / DAO-Auth).

```
Plataforma-Delphos/
├── src/                  # React frontend (Vite)
│   ├── screens/          # Screen1Register … Screen8Profile
│   └── services/         # api.js, authService.js
├── DAO-Auth-main/        # FastAPI backend (Docker)
│   ├── app/              # api, core, db, models, repositories, schemas, services
│   ├── docker-compose.yml
│   └── alembic/          # DB migrations
├── index.html
├── vite.config.js
└── package.json
```

## Requirements

- **Node.js** ≥ 20 (tested on v24.10.0)
- **Docker** + Docker Compose (for backend + Postgres)
- The frontend talks to the backend at `http://localhost:8000` by default. Override with `VITE_API_URL`.

## First-time setup

```bash
# 1. Install frontend dependencies
npm install

# 2. Build the backend image and create containers (first time only)
cd DAO-Auth-main
docker compose up -d
cd ..
```

The first `docker compose up` builds the API image, creates `aurum_postgres` + `aurum_api`, runs Alembic migrations and starts uvicorn on port 8000.

## Daily startup

Two terminals (or run both in background):

```bash
# Terminal 1 — Backend (FastAPI + Postgres)
cd DAO-Auth-main
docker compose start         # if containers already exist
# or: docker compose up -d   # first run / after config changes

# Terminal 2 — Frontend (Vite dev server)
npm run dev
```

Services:

| Service   | URL                        | Notes                              |
| --------- | -------------------------- | ---------------------------------- |
| Frontend  | http://localhost:5173      | Vite dev server, HMR enabled       |
| Backend   | http://localhost:8000      | FastAPI                            |
| Health    | http://localhost:8000/health | Should return `200`             |
| API docs  | http://localhost:8000/docs | Swagger UI                         |
| Postgres  | localhost:5432             | user/pass: `postgres` / `postgres` |
| pgAdmin   | http://localhost:5050      | Optional, `docker compose --profile tools up -d` |

## Stopping

```bash
# Stop the frontend: Ctrl+C in its terminal (or kill the background job)
# Stop the backend:
cd DAO-Auth-main
docker compose stop          # keep data
# or: docker compose down    # remove containers (keeps the named volume)
```

## Troubleshooting

- **`vite: command not found`** — run `npm install` in the repo root.
- **`Container "aurum_postgres" is already in use`** — old containers exist from a previous run. Use `docker start aurum_postgres aurum_api`, or remove them with `docker rm -f aurum_postgres aurum_api` and `docker compose up -d` again.
- **`npm` not on PATH** — Node is installed via nvm; activate it with `nvm use 24` (or add `~/.nvm/versions/node/<version>/bin` to `PATH`).
- **Backend can't reach DB** — confirm both containers are healthy: `docker ps --filter name=aurum`.
- **Reset the database** — `docker compose down -v` (drops the `postgres_data` volume), then `docker compose up -d` to re-run migrations from scratch.

## Frontend → backend wiring

`src/services/api.js` creates an Axios instance pointed at `VITE_API_URL` (default `http://localhost:8000`) and attaches the JWT from `localStorage` as `Authorization: Bearer …`. To point the frontend at a different backend, create a `.env` file in the repo root:

```
VITE_API_URL=http://localhost:8000
```

## More backend details

See `DAO-Auth-main/README.md` for the full backend documentation (architecture, phases, tests, deployment).
