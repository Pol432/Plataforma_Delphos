# Oracle

Los tres subsistemas de IA de la Plataforma Delphos:

- **recommendation/** — Wide & Deep para recomendación de carreras (MindSpore).
- **learning_path/** — optimizador de rutas de aprendizaje / currículum.
- **skill_graph/** — grafo temporal de habilidades (inferencia y taxonomía).

Por ahora son **independientes**: cada uno tiene su propio `requirements.txt` y se
ejecuta por separado. No están fusionados en un único servicio todavía.

## Probar el oráculo

`./test_oracle.sh` monta lo que falte, corre todo lo que sea ejecutable en la
máquina y dice explícitamente qué se ha saltado y por qué. No hace falta
conocer los entornos de `oracle/` para usarlo.

```bash
./oracle/test_oracle.sh                # todo
./oracle/test_oracle.sh api            # sólo los endpoints (backend vivo)
./oracle/test_oracle.sh learning-path  # sólo un subsistema
./oracle/test_oracle.sh setup          # sólo preparar los venv
./oracle/test_oracle.sh --help
```

Opciones útiles: `--no-setup` (no toca los venv, mucho más rápido en
ejecuciones repetidas), `--api-url URL` y `--with-mindspore` (instalación
pesada, exige Python ≤3.11).

Sale **0** si nada falló. Un `SKIP` no hace fallar el script pero **no es un
`PASS`**: significa que eso no se ha verificado en esa máquina.

| Objetivo | Qué corre | Qué necesita |
|---|---|---|
| `learning-path` | 61 tests + construcción del grafo + demo | sólo Python 3.10+ |
| `recommendation`| 47 tests (9 se saltan sin MindSpore) | Python 3.10+; MindSpore sólo con Python ≤3.11 |
| `skill-graph` | inferencia por texto y cuestionario | sólo Python 3; el e2e pide PostgreSQL + MindSpore |
| `api` | los 4 endpoints `/api/v1/oracle/*` | backend levantado (`./dev.sh`) |
| `backend` | `tests/oracle` y `tests/ml_engine` | Docker con el contenedor `web` arriba |

Los scripts de `scripts/` se pueden lanzar sueltos, y los de Python **sólo usan
la librería estándar** — sin venv ni instalar nada:

```bash
./oracle/scripts/run_tests.sh                          # la suite del backend contra Postgres
python3 oracle/scripts/smoke_api.py                    # 41 comprobaciones sobre la API
python3 oracle/scripts/check_skill_graph_offline.py    # skill_graph sin base de datos
```

Detalle de cada uno, qué significa un resultado sano y qué dejan detrás:
`oracle/scripts/README.md`.

`smoke_api.py` comprueba, además de que los endpoints respondan, que la
respuesta de `/recommend` **declara la procedencia de sus números**
(`scored_by` = heurístico, `ranked_by` = modelo). Es la confusión más fácil de
cometer al integrar: ver "Estado conocido" en el README raíz.

### Lo que estos scripts no cubren

- El end-to-end de `skill_graph` corre con **pesos aleatorios** mientras falte
  `checkpoints/task_eval_model.ckpt`.
- Las métricas de `recommendation` (AUC 0.7763) **no son reproducibles**: el
  MindRecord de test no está versionado.

`skill_taxonomy` no aparece en las comprobaciones offline a propósito: llama a
`load_skill_catalog()` en tiempo de import, así que sin PostgreSQL no es ni
importable.
