# Scripts de verificación del oráculo

Para comprobar que el subsistema de IA sigue funcionando sin tener que
reconstruir comandos `curl` a mano ni acordarse de qué había que mirar.

No hace falta contexto previo ni montar los entornos de Python de `oracle/`:
los dos scripts principales sólo necesitan Docker, y el smoke test tira de la
librería estándar de Python (nada que instalar).

```bash
./oracle/scripts/run_tests.sh          # la suite del backend contra Postgres
python3 oracle/scripts/smoke_api.py    # los endpoints, contra el stack vivo
```

Los dos salen **0 si todo va bien** y distinto de 0 si algo falla, así que
sirven tal cual para CI.

---

## `run_tests.sh` — la suite del backend contra PostgreSQL

Levanta el stack si no estaba, crea la base `aurum_test` si no existía y corre
`pytest` dentro del contenedor.

**Por qué existe:** la suite por defecto corre contra SQLite en fichero, que no
cubre ni los tipos de columna reales ni la semántica nativa de las claves
ajenas. Este script fija `TEST_DATABASE_URL` al Postgres del compose para que
sí se cubran. Es fácil olvidarse de esa variable y creer que has probado más de
lo que has probado.

```bash
./oracle/scripts/run_tests.sh                # toda la suite
./oracle/scripts/run_tests.sh tests/oracle   # sólo un subdirectorio
./oracle/scripts/run_tests.sh --sqlite       # más rápido, cubre menos
./oracle/scripts/run_tests.sh --no-start     # falla si el stack no está ya arriba
./oracle/scripts/run_tests.sh --help
```

Resultado sano, hoy:

```
Resumen
  passed  443
  failed  0
  errors  0
  skipped 19   (un SKIP no es un PASS: eso no se ha verificado)
  motor   PostgreSQL (aurum_test)
  ✓ la suite pasó
```

Los 19 saltados son tests que piden cosas que no están en esta máquina
(MindSpore, sobre todo). Que estén saltados es lo normal; que **crezcan** de
golpe no lo es.

La primera ejecución compila la imagen y tarda varios minutos. Las siguientes,
unos segundos.

---

## `smoke_api.py` — los endpoints contra el stack vivo

Comprueba que `/api/v1/oracle/*` responde **lo que se espera hoy**, no sólo que
responde. Necesita el stack levantado (`./dev.sh start`).

```bash
python3 oracle/scripts/smoke_api.py
python3 oracle/scripts/smoke_api.py --api-url http://localhost:8000
python3 oracle/scripts/smoke_api.py --no-fallback   # sin tocar Docker
```

Cada línea dice PASS o FAIL con lo que esperaba y lo que encontró. Resultado
sano, hoy: **41/41 comprobaciones pasaron.**

Lo que mira, por secciones:

| Sección | Qué comprueba |
|---|---|
| 0–1 | Login, y que los endpoints rechazan peticiones sin token |
| 2 · `/catalog` | 200 y **64 simulaciones** |
| 3 · `/skills` | 200, **68 entradas**, `canonical_name` en todas, y que el grupo `id=39` sea un canónico (*Adobe Creative Suite*) con dos alias (*Figma*, *Photoshop*) apuntándole |
| 4 · `/recommend` | 200, `engine`=`wide_and_deep`, `scored_by`=`heuristic_bridge_v1`, `ranked_by`=`wide_and_deep`, `confidence_interval` null en todos los items, y que el modelo **reordena de verdad** |
| 5 | Validación de entrada (`top_n` fuera de rango, skill desconocida) |
| 6 · `/full_profile` | 200, los tres campos de procedencia en `heuristic_bridge_v1`, `confidence_interval` null, y que exista el campo `learning_paths` (hoy `[]`) |
| 7 · OOV | Que `sim_ux_designer` y `sim_project_manager` traigan `matched_skills` no vacío |
| 8 · Fallback | Apaga el modelo, comprueba que la API cae al heurístico sin romperse, y lo vuelve a encender |

### Tres cosas que conviene entender antes de leer la salida

**Los números no los calcula el modelo.** Aunque `engine` diga `wide_and_deep`,
todos los valores de `scores` los produce el heurístico; el modelo sólo decide
el **orden**. Por eso `scored_by` y `ranked_by` son campos distintos, y por eso
el script los comprueba por separado. No presentes `engagement_probability`
como salida del modelo entrenado.

**`confidence_interval` va en null a propósito.** No hay estimación de
incertidumbre detrás. Si algún día sale con un número, es que alguien lo ha
fabricado: por eso hay un check dedicado.

**Que el orden NO coincida con `engagement_probability` descendente es lo
correcto.** Es la prueba de que el modelo está reordenando y no dejando pasar
la lista del heurístico. El script pide el catálogo entero (64) para esto: con
3 items podrían salir en orden por casualidad. Hoy difieren 59 de 64 posiciones.

### Si algo falla

- **`engine` es `heuristic_bridge_v1` cuando se esperaba `wide_and_deep`** — el
  modelo no se ha cargado y la API ha caído al heurístico. No está "roto" (por
  eso el resto pasa), pero no es el estado esperado. Mira el log:
  `docker compose -f backend/docker-compose.yml logs web | grep -i wide`, y
  comprueba que `ORACLE_ENGINE` valga `auto`.
- **`matched_skills` vacío en la sección 7** — ha vuelto la regresión del mapeo
  OOV: las skills del perfil no se están resolviendo contra el catálogo.
- **Cambian los conteos de 64 o 68** — puede ser legítimo (una simulación
  nueva, el vocabulario que crece). Si lo es, actualiza `N_SIMULACIONES` /
  `N_SKILLS` en la cabecera de `smoke_api.py`. Que el script se queje ante un
  cambio no anunciado es lo que se busca.

---

## `check_skill_graph_offline.py`

Comprueba `skill_graph` sin base de datos ni backend levantado. Útil cuando
sólo quieres saber si esa parte importa y corre.

```bash
python3 oracle/scripts/check_skill_graph_offline.py
```

---

## Qué dejan detrás

Nada que sorprenda a quien los corra después:

- **El stack se queda levantado.** Es lo que quieres si acabas de correr los
  tests y sigues trabajando. Se para con `./dev.sh stop`.
- **La base `aurum_test`** se crea si no existía y se reutiliza. Las tablas se
  crean y se borran en cada ejecución; los datos de desarrollo de `aurum_dao`
  no se tocan.
- **El usuario `oracle_smoke`** (`oracle_smoke@test.dev`) se crea la primera
  vez y se reutiliza después. No se borra —no hay endpoint para ello— pero es
  siempre el mismo y el nombre lo delata como artefacto de pruebas.
- **La sección 8 reinicia el contenedor `web` dos veces** y lo deja como
  estaba. La restauración va en un `finally`: aunque el script falle o lo
  cortes con Ctrl-C, `ORACLE_ENGINE` vuelve a `auto`. Con `--no-fallback` no se
  toca nada.

## Y además

`./oracle/test_oracle.sh` corre los tres subsistemas de IA (learning path,
recommendation, skill graph) además de los endpoints. Es más lento y algunas
partes se saltan según la máquina. Ver `oracle/README.md`.
