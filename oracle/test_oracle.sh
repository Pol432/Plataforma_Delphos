#!/usr/bin/env bash
# ============================================================================
# Plataforma Delphos — batería de pruebas de la sección oracle/ (IA)
# ----------------------------------------------------------------------------
# Pensado para que Alex y Matías puedan verificar el oráculo sin conocer sus
# entornos: el script monta lo que falta, corre lo que se puede correr en esta
# máquina y dice explícitamente qué se ha saltado y por qué.
#
#   ./oracle/test_oracle.sh                todo lo que sea posible aquí
#   ./oracle/test_oracle.sh learning-path  sólo el optimizador de rutas
#   ./oracle/test_oracle.sh recommendation sólo el Wide & Deep
#   ./oracle/test_oracle.sh skill-graph    sólo el grafo temporal
#   ./oracle/test_oracle.sh api            endpoints /api/v1/oracle/* (backend vivo)
#   ./oracle/test_oracle.sh backend        tests de oracle dentro del contenedor
#   ./oracle/test_oracle.sh setup          sólo preparar los venv, sin probar
#
# Opciones:
#   --api-url URL      URL del backend (por defecto http://localhost:8000)
#   --with-mindspore   intenta instalar MindSpore en recommendation/ (pesado,
#                      exige Python <=3.11); sin esto se usa el entorno ligero
#   --no-setup         no crea ni actualiza venv, usa lo que ya haya
#   -h | --help        esta ayuda
#
# Código de salida: 0 si nada falló. Los SKIP no hacen fallar el script, pero
# se listan aparte para que nunca se confundan con un PASS.
# ============================================================================

set -uo pipefail

ORACLE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$ORACLE/.." && pwd)"
BACKEND="$ROOT/backend"

API_URL="http://localhost:8000"
WITH_MINDSPORE=0
DO_SETUP=1

C_INFO='\033[36m'; C_OK='\033[32m'; C_WARN='\033[33m'; C_ERR='\033[31m'
C_BOLD='\033[1m'; C_OFF='\033[0m'

say()  { printf "${C_INFO}==>${C_OFF} %s\n" "$*"; }
ok()   { printf "  ${C_OK}✓${C_OFF} %s\n" "$*"; }
warn() { printf "  ${C_WARN}!${C_OFF} %s\n" "$*"; }
bad()  { printf "  ${C_ERR}✗${C_OFF} %s\n" "$*"; }
head() { printf "\n${C_BOLD}%s${C_OFF}\n" "$*"; }

# --- registro de resultados -------------------------------------------------
# Se acumulan como "ESTADO|componente|detalle" y se vuelcan en el resumen.
RESULTS=()
record() { RESULTS+=("$1|$2|$3"); }
pass_c() { ok   "$2"; record PASS "$1" "$2"; }
fail_c() { bad  "$2"; record FAIL "$1" "$2"; }
skip_c() { warn "$2"; record SKIP "$1" "$2"; }

# Imprime la cabecera de este fichero: todo el bloque de comentarios que sigue
# al shebang, hasta la primera línea que ya no es comentario.
usage() {
  local line
  while IFS= read -r line; do
    [[ "$line" == \#!* ]] && continue
    [[ "$line" == \#* ]] || break
    printf '%s\n' "${line/#\# /}" | sed 's/^#$//'
  done <"${BASH_SOURCE[0]}"
  exit 0
}

# --- utilidades -------------------------------------------------------------

# Primer intérprete disponible que sirva para MindSpore (necesita <=3.11).
find_legacy_python() {
  local c
  for c in python3.11 python3.10; do
    command -v "$c" >/dev/null 2>&1 && { echo "$c"; return 0; }
  done
  return 1
}

# Un venv se rompe si el Python del sistema se actualiza por debajo (típico en
# Arch): los binarios siguen ahí pero site-packages apunta a la versión vieja.
# Se detecta comparando pyvenv.cfg con la versión real del intérprete.
venv_healthy() {
  local venv="$1"
  [[ -x "$venv/bin/python" ]] || return 1
  "$venv/bin/python" -c 'import sys' >/dev/null 2>&1 || return 1
  local real cfg
  real="$("$venv/bin/python" -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null)"
  cfg="$(sed -n 's/^version *= *\([0-9]*\.[0-9]*\).*/\1/p' "$venv/pyvenv.cfg" 2>/dev/null)"
  [[ -z "$cfg" || "$real" == "$cfg" ]]
}

# Crea el venv si falta o si está roto. $1 destino, $2 intérprete base.
ensure_venv() {
  local venv="$1" py="${2:-python3}"
  if venv_healthy "$venv"; then
    return 0
  fi
  if [[ -d "$venv" ]]; then
    warn "el venv de $(basename "$(dirname "$venv")") está roto — se rehace"
    rm -rf "$venv"
  fi
  "$py" -m venv "$venv" || return 1
  "$venv/bin/pip" install --upgrade pip -q 2>/dev/null
}

# ============================================================================
# learning_path — optimizador de rutas. Sin base de datos ni GPU: es el único
# de los tres que se puede probar entero en cualquier máquina.
# ============================================================================
run_learning_path() {
  head "learning_path — optimizador de rutas de aprendizaje"
  local dir="$ORACLE/learning_path" venv="$ORACLE/learning_path/.venv"
  local comp="learning_path"

  if [[ $DO_SETUP -eq 1 ]]; then
    say "preparando entorno"
    if ! ensure_venv "$venv"; then
      fail_c "$comp" "no se pudo crear el venv"; return
    fi
    if ! "$venv/bin/pip" install -q -r "$dir/requirements.txt"; then
      fail_c "$comp" "falló la instalación de requirements.txt"; return
    fi
    ok "dependencias instaladas"
  elif ! venv_healthy "$venv"; then
    skip_c "$comp" "sin venv utilizable (quita --no-setup para crearlo)"; return
  fi

  # Paso obligatorio: data/skill_graph_v1.json no está versionado. Sin él los
  # tests y el demo fallan con FileNotFoundError.
  say "generando data/skill_graph_v1.json"
  if (cd "$dir" && "$venv/bin/python" -m learning_path.core.build_initial_graph >/dev/null 2>&1); then
    pass_c "$comp · grafo" "grafo inicial generado"
  else
    fail_c "$comp · grafo" "falló build_initial_graph (los tests dependen de él)"
    return
  fi

  say "tests"
  local out
  out="$(cd "$dir" && "$venv/bin/python" -m pytest tests/ -q 2>&1)"
  if [[ $? -eq 0 ]]; then
    pass_c "$comp · tests" "$(echo "$out" | tail -1)"
  else
    fail_c "$comp · tests" "$(echo "$out" | tail -1)"
    echo "$out" | tail -25
  fi

  say "demo end-to-end"
  if (cd "$dir" && "$venv/bin/python" scripts/demo.py >/dev/null 2>&1); then
    pass_c "$comp · demo" "scripts/demo.py corre entero"
  else
    fail_c "$comp · demo" "scripts/demo.py falló"
  fi
}

# ============================================================================
# recommendation — Wide & Deep (MindSpore). MindSpore no publica wheels para
# Python 3.12+, así que por defecto se monta el entorno ligero: los tests que
# piden el framework se saltan solos.
# ============================================================================
run_recommendation() {
  head "recommendation — Wide & Deep para recomendación de carreras"
  local dir="$ORACLE/recommendation" venv="$ORACLE/recommendation/.venv"
  local comp="recommendation" base_py="python3" modo="ligero (sin MindSpore)"

  if [[ $WITH_MINDSPORE -eq 1 ]]; then
    local legacy
    if legacy="$(find_legacy_python)"; then
      base_py="$legacy"; modo="completo (con MindSpore, $legacy)"
      say "usando $legacy para poder instalar MindSpore"
    else
      warn "no hay python3.10/3.11 en el PATH — MindSpore no se puede instalar"
      warn "se sigue con el entorno ligero"
    fi
  fi

  if [[ $DO_SETUP -eq 1 ]]; then
    say "preparando entorno $modo"
    if ! ensure_venv "$venv" "$base_py"; then
      fail_c "$comp" "no se pudo crear el venv"; return
    fi
    if [[ "$modo" == completo* ]]; then
      # MindSpore puede no estar en PyPI para esta plataforma; requirements.txt
      # documenta el índice de Huawei como alternativa.
      if ! "$venv/bin/pip" install -q -r "$dir/requirements.txt"; then
        warn "falló la instalación completa — se cae al entorno ligero"
        warn "si tu plataforma no está en PyPI, mira el índice de Huawei en requirements.txt"
        "$venv/bin/pip" install -q pytest numpy pandas scikit-learn || {
          fail_c "$comp" "falló también la instalación ligera"; return; }
      fi
    else
      # Lo mínimo para la suite: el resto de tests son numpy puro.
      if ! "$venv/bin/pip" install -q pytest numpy pandas scikit-learn; then
        fail_c "$comp" "falló la instalación de dependencias"; return
      fi
    fi
    ok "dependencias instaladas"
  elif ! venv_healthy "$venv"; then
    skip_c "$comp" "sin venv utilizable (quita --no-setup para crearlo)"; return
  fi

  if "$venv/bin/python" -c 'import mindspore' >/dev/null 2>&1; then
    ok "MindSpore disponible — la suite corre completa"
  else
    warn "MindSpore no disponible — los tests que lo piden se saltarán solos"
  fi

  say "tests"
  local out
  out="$(cd "$dir" && "$venv/bin/python" -m pytest tests/ -q 2>&1)"
  local rc=$?
  local resumen; resumen="$(echo "$out" | grep -E '[0-9]+ (passed|failed)' | tail -1)"
  if [[ $rc -eq 0 ]]; then
    pass_c "$comp · tests" "${resumen:-sin resumen}"
    if echo "$resumen" | grep -q skipped; then
      warn "los tests saltados son los que exigen MindSpore: no se han verificado"
    fi
  else
    fail_c "$comp · tests" "${resumen:-fallo}"
    echo "$out" | tail -25
  fi

  # El checkpoint carga, pero su AUC no se puede reconfirmar: el MindRecord de
  # test no está versionado. Que los tests pasen no valida las métricas.
  if [[ -f "$dir/README_CHECKPOINT_STATUS.md" ]]; then
    warn "métricas no reproducibles: falta el MindRecord de test"
    warn "  detalle en oracle/recommendation/README_CHECKPOINT_STATUS.md"
  fi
}

# ============================================================================
# skill_graph — grafo temporal. Es el más limitado: exige PostgreSQL propio,
# MindSpore y un checkpoint que no existe en el repo.
# ============================================================================
run_skill_graph() {
  head "skill_graph — grafo temporal de habilidades"
  local dir="$ORACLE/skill_graph" comp="skill_graph"

  # Aviso primero: aunque todo lo demás pase, las predicciones no significan
  # nada mientras falte el checkpoint.
  if [[ ! -f "$dir/checkpoints/task_eval_model.ckpt" ]]; then
    warn "falta checkpoints/task_eval_model.ckpt — el modelo cae a pesos"
    warn "  ALEATORIOS: sus predicciones no significan nada todavía"
    warn "  detalle en oracle/skill_graph/README_CHECKPOINT_STATUS.md"
  fi

  # Lo verificable sin base de datos: inferencia por texto (regex pura) y el
  # cuestionario de onboarding. Ojo: `skill_taxonomy` NO entra aquí porque
  # consulta PostgreSQL en tiempo de import — sin base no es ni importable.
  # Sólo necesita la stdlib, así que va con el python del sistema.
  say "comprobaciones sin base de datos"
  if python3 "$ORACLE/scripts/check_skill_graph_offline.py"; then
    pass_c "$comp · offline" "inferencia por texto y cuestionario correctos"
  else
    fail_c "$comp · offline" "falló alguna comprobación offline"
  fi

  local venv="$dir/.venv"
  if [[ $DO_SETUP -eq 1 ]]; then
    ensure_venv "$venv" && "$venv/bin/pip" install -q numpy python-dotenv 2>/dev/null
  fi

  # El e2e real necesita las tres cosas a la vez.
  say "end-to-end"
  local motivos=()
  [[ -f "$dir/.env" ]] || [[ -n "${DATABASE_URL:-}" ]] || motivos+=("falta DATABASE_URL (crea oracle/skill_graph/.env)")
  if venv_healthy "$venv"; then
    "$venv/bin/python" -c 'import mindspore' >/dev/null 2>&1 || motivos+=("falta MindSpore (necesita Python <=3.11)")
    "$venv/bin/python" -c 'import sentence_transformers' >/dev/null 2>&1 || motivos+=("falta sentence-transformers")
  else
    motivos+=("sin venv utilizable")
  fi

  if [[ ${#motivos[@]} -gt 0 ]]; then
    local m
    for m in "${motivos[@]}"; do warn "$m"; done
    skip_c "$comp · e2e" "no ejecutable aquí: ${motivos[0]}"
    warn "para correrlo hace falta: PostgreSQL con db/migrations/*.sql aplicadas,"
    warn "  DATABASE_URL en un .env, y MindSpore + sentence-transformers"
    return
  fi

  local out
  out="$(cd "$dir" && "$venv/bin/python" tests/test_e2e.py 2>&1)"
  if [[ $? -eq 0 ]]; then
    pass_c "$comp · e2e" "test_e2e.py corre entero"
  else
    fail_c "$comp · e2e" "test_e2e.py falló"
    echo "$out" | tail -25
  fi
}

# ============================================================================
# API — los endpoints que consumen frontend y backend. Sin venv: stdlib.
# ============================================================================
run_api() {
  head "API — endpoints /api/v1/oracle/*"
  if ! curl -fsS -m 5 "$API_URL/" >/dev/null 2>&1; then
    skip_c "api" "el backend no responde en $API_URL (levántalo con ./dev.sh)"
    return
  fi
  ok "backend vivo en $API_URL"

  if python3 "$ORACLE/scripts/smoke_api.py" --api-url "$API_URL"; then
    pass_c "api" "los endpoints del oráculo responden y son coherentes"
  else
    fail_c "api" "alguna comprobación de los endpoints falló"
  fi
}

# ============================================================================
# backend — tests de oracle del backend, dentro del contenedor.
# ============================================================================
run_backend() {
  head "backend — tests de oracle y ml_engine"
  if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
    skip_c "backend" "Docker no está disponible"; return
  fi
  if ! docker compose -f "$BACKEND/docker-compose.yml" ps --status running 2>/dev/null | grep -q web; then
    skip_c "backend" "el contenedor web no está levantado (./dev.sh)"; return
  fi

  local out
  out="$(docker compose -f "$BACKEND/docker-compose.yml" exec -T web \
          pytest tests/oracle tests/ml_engine -q 2>&1)"
  local rc=$?
  local resumen; resumen="$(echo "$out" | grep -E '[0-9]+ (passed|failed)' | tail -1)"
  if [[ $rc -eq 0 ]]; then
    pass_c "backend · tests" "${resumen:-ok}"
  else
    fail_c "backend · tests" "${resumen:-fallo}"
    echo "$out" | tail -25
  fi
}

# ============================================================================
# Resumen
# ============================================================================
summary() {
  head "Resumen"
  local n_pass=0 n_fail=0 n_skip=0 line estado comp detalle color
  # printf cuenta BYTES, y "·" ocupa dos: rellenar a mano con ${#comp}, que en
  # un locale UTF-8 cuenta caracteres, mantiene la columna cuadrada.
  for line in "${RESULTS[@]}"; do
    IFS='|' read -r estado comp detalle <<<"$line"
    case "$estado" in
      PASS) n_pass=$((n_pass+1)); color="$C_OK" ;;
      FAIL) n_fail=$((n_fail+1)); color="$C_ERR" ;;
      SKIP) n_skip=$((n_skip+1)); color="$C_WARN" ;;
      *)    continue ;;
    esac
    local relleno=""
    (( ${#comp} < 26 )) && printf -v relleno '%*s' $((26 - ${#comp})) ''
    printf "  ${color}%s${C_OFF}  %s%s %s\n" "$estado" "$comp" "$relleno" "$detalle"
  done

  echo
  printf "  %d pasaron · %d fallaron · %d saltados\n" "$n_pass" "$n_fail" "$n_skip"

  if [[ $n_skip -gt 0 ]]; then
    printf "\n${C_WARN}Un SKIP no es un PASS:${C_OFF} eso no se ha verificado en esta máquina.\n"
  fi

  # Estos límites son del proyecto, no del script: conviene repetirlos aquí
  # para que no se lea "todo verde" como "el oráculo está validado".
  printf "\n${C_BOLD}Límites conocidos (no los arregla este script):${C_OFF}\n"
  cat <<'EOF'
  · skill_graph corre con pesos ALEATORIOS: falta task_eval_model.ckpt.
  · Las métricas de recommendation (AUC 0.7763) no son reproducibles:
    el MindRecord de test no está versionado.
  · En /oracle/recommend los números visibles los calcula el heurístico,
    no el Wide&Deep — el modelo sólo decide el orden. `confidence_interval`
    es una banda fija, no una estimación de incertidumbre.
EOF

  [[ $n_fail -eq 0 ]]
}

# ============================================================================
# Argumentos y despacho
# ============================================================================
TARGETS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)       usage ;;
    --api-url)       API_URL="${2:?--api-url necesita una URL}"; shift 2 ;;
    --with-mindspore) WITH_MINDSPORE=1; shift ;;
    --no-setup)      DO_SETUP=0; shift ;;
    -*)              bad "opción desconocida: $1"; exit 2 ;;
    *)               TARGETS+=("$1"); shift ;;
  esac
done

[[ ${#TARGETS[@]} -eq 0 ]] && TARGETS=(all)

printf "${C_BOLD}Plataforma Delphos · pruebas de la sección oracle/${C_OFF}\n"
printf "Raíz: %s\n" "$ROOT"

for target in "${TARGETS[@]}"; do
  case "$target" in
    all)
      run_learning_path; run_recommendation; run_skill_graph
      run_api; run_backend ;;
    setup)
      DO_SETUP=1
      head "Preparando entornos"
      ensure_venv "$ORACLE/learning_path/.venv"   && "$ORACLE/learning_path/.venv/bin/pip" install -q -r "$ORACLE/learning_path/requirements.txt" && ok "learning_path listo"
      ensure_venv "$ORACLE/recommendation/.venv"  && "$ORACLE/recommendation/.venv/bin/pip" install -q pytest numpy pandas scikit-learn && ok "recommendation listo (entorno ligero)"
      ensure_venv "$ORACLE/skill_graph/.venv"     && "$ORACLE/skill_graph/.venv/bin/pip" install -q numpy python-dotenv && ok "skill_graph listo (sólo comprobación estática)"
      echo; ok "entornos preparados — ahora: ./oracle/test_oracle.sh --no-setup"
      exit 0 ;;
    learning-path|learning_path|lp) run_learning_path ;;
    recommendation|rec)             run_recommendation ;;
    skill-graph|skill_graph|sg)     run_skill_graph ;;
    api)                            run_api ;;
    backend)                        run_backend ;;
    *) bad "objetivo desconocido: $target"
       echo "Usa: all | setup | learning-path | recommendation | skill-graph | api | backend"
       exit 2 ;;
  esac
done

summary
