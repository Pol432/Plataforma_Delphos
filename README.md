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

## Notas

- Los checkpoints (`*.ckpt`) **sí** se versionan por ahora — son pequeños.
- `node_modules/` y `.venv/` no se copiaron ni se versionan: reinstalar con
  `npm install` (frontend) y `pip install -r requirements.txt` (backend/oracle).
