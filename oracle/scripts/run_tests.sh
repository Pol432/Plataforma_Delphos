#!/usr/bin/env bash
# ============================================================================
# Plataforma Delphos — suite completa del backend contra PostgreSQL real
# ----------------------------------------------------------------------------
# Levanta el stack si hace falta y corre `pytest` dentro del contenedor `web`.
# La suite corre siempre contra Postgres (ver `backend/tests/conftest.py`, que
# ya lo usa por defecto); este script además se encarga de levantar el stack y
# de esperar a que la base acepte conexiones.
#
#   ./oracle/scripts/run_tests.sh              toda la suite
#   ./oracle/scripts/run_tests.sh tests/oracle sólo un subdirectorio
#   ./oracle/scripts/run_tests.sh -h
#
# Opciones:
#   --no-start    no levanta nada; falla si el stack no está ya arriba.
#   -h | --help   esta ayuda
#
# No hace falta preparación manual: comprueba los prerequisitos y dice qué
# falta en vez de reventar con un error críptico. Sale 0 sólo si no falló
# ningún test, así que sirve tal cual en CI.
# ============================================================================

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
COMPOSE_FILE="$ROOT/backend/docker-compose.yml"

# Base de datos separada a propósito: la suite hace create_all/drop_all al
# empezar y acabar, así que apuntarla a `aurum_dao` borraría los datos de
# desarrollo de quien la corra.
TEST_DB="aurum_test"
TEST_DATABASE_URL="postgresql://postgres:postgres@db:5432/$TEST_DB"

DO_START=1
PYTEST_ARGS=()

C_INFO='\033[36m'; C_OK='\033[32m'; C_WARN='\033[33m'; C_ERR='\033[31m'
C_BOLD='\033[1m'; C_OFF='\033[0m'

say()  { printf "${C_INFO}==>${C_OFF} %s\n" "$*"; }
ok()   { printf "  ${C_OK}✓${C_OFF} %s\n" "$*"; }
warn() { printf "  ${C_WARN}!${C_OFF} %s\n" "$*"; }
bad()  { printf "  ${C_ERR}✗${C_OFF} %s\n" "$*"; }

# Imprime la cabecera de este fichero como ayuda.
usage() {
  local line
  while IFS= read -r line; do
    [[ "$line" == \#!* ]] && continue
    [[ "$line" == \#* ]] || break
    printf '%s\n' "${line:2}"
  done < "${BASH_SOURCE[0]}"
}

# Explica qué falta y cómo arreglarlo, en vez de dejar que falle el comando.
die_missing() {
  bad "$1"
  shift
  local hint
  for hint in "$@"; do printf "      %s\n" "$hint"; done
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)  usage; exit 0 ;;
    --no-start) DO_START=0; shift ;;
    *)          PYTEST_ARGS+=("$1"); shift ;;
  esac
done

# --- 1. Prerequisitos -------------------------------------------------------
say "Comprobando prerequisitos"

command -v docker >/dev/null 2>&1 || die_missing \
  "docker no está instalado (o no está en el PATH)." \
  "Instálalo: https://docs.docker.com/engine/install/"

docker compose version >/dev/null 2>&1 || die_missing \
  "este docker no trae el plugin 'compose' (v2)." \
  "Comprueba con: docker compose version" \
  "En Debian/Ubuntu: sudo apt install docker-compose-plugin"

docker info >/dev/null 2>&1 || die_missing \
  "el demonio de Docker no responde." \
  "Arráncalo:      sudo systemctl start docker" \
  "Si es de permisos, añádete al grupo: sudo usermod -aG docker \$USER" \
  "(hay que volver a iniciar sesión para que surta efecto)"

[[ -f "$COMPOSE_FILE" ]] || die_missing \
  "no encuentro $COMPOSE_FILE." \
  "¿Estás en el repo Plataforma_Delphos?"

ok "docker, compose y el demonio responden"

DC=(docker compose -f "$COMPOSE_FILE")

# --- 2. Stack arriba --------------------------------------------------------
# `ps -q web` vacío = el servicio no tiene contenedor corriendo.
web_up() { [[ -n "$("${DC[@]}" ps -q web 2>/dev/null)" ]]; }

if web_up; then
  ok "el stack ya estaba levantado (no lo toco)"
else
  if [[ $DO_START -eq 0 ]]; then
    die_missing "el stack no está levantado y me has pasado --no-start." \
                "Levántalo con: ./dev.sh start"
  fi
  say "Levantando el stack (la primera vez compila la imagen, tarda)"
  if ! "${DC[@]}" up -d --build db web; then
    bad "no se pudo levantar el stack"
    printf "      Mira el log con: docker compose -f %s logs web\n" "$COMPOSE_FILE"
    exit 2
  fi
  ok "stack levantado"
fi

# `pytest --version` dentro del contenedor sirve de doble comprobación: que el
# contenedor acepta comandos y que la suite está instalada.
say "Esperando a que el contenedor web acepte comandos"
for _ in $(seq 1 60); do
  "${DC[@]}" exec -T web pytest --version >/dev/null 2>&1 && break
  sleep 1
done
if ! "${DC[@]}" exec -T web pytest --version >/dev/null 2>&1; then
  bad "el contenedor web no responde (o no tiene pytest) tras 60 s"
  printf "      Mira el log con: docker compose -f %s logs web\n" "$COMPOSE_FILE"
  exit 2
fi
ok "contenedor web listo"

# --- 3. Base de datos de test ----------------------------------------------
say "Preparando la base de datos de test ($TEST_DB)"

for _ in $(seq 1 30); do
  "${DC[@]}" exec -T db pg_isready -U postgres >/dev/null 2>&1 && break
  sleep 1
done
if ! "${DC[@]}" exec -T db pg_isready -U postgres >/dev/null 2>&1; then
  bad "Postgres no acepta conexiones tras 30 s"
  printf "      Mira el log con: docker compose -f %s logs db\n" "$COMPOSE_FILE"
  exit 2
fi

# create_all/drop_all crea las TABLAS, pero la base de datos tiene que
# existir antes. conftest.py también sabe crearla (para quien corra `pytest`
# a secas), pero hacerlo aquí da un error claro si Postgres no coopera.
# Idempotente: si ya está, no se toca ni se borra al acabar.
if "${DC[@]}" exec -T db psql -U postgres -tAc \
     "SELECT 1 FROM pg_database WHERE datname='$TEST_DB'" 2>/dev/null | grep -q 1; then
  ok "la base $TEST_DB ya existía"
else
  if "${DC[@]}" exec -T db createdb -U postgres "$TEST_DB" >/dev/null 2>&1; then
    ok "base $TEST_DB creada"
  else
    bad "no se pudo crear la base $TEST_DB"
    exit 2
  fi
fi

PYTEST_ENV=(-e "TEST_DATABASE_URL=$TEST_DATABASE_URL")
MOTOR="PostgreSQL ($TEST_DB)"

# --- 4. La suite ------------------------------------------------------------
printf "\n${C_BOLD}Suite del backend${C_OFF}\n"
printf "  motor: %s\n" "$MOTOR"
printf "  args : %s\n\n" "${PYTEST_ARGS[*]:-(toda la suite)}"

OUT="$(mktemp)"
# `trap` y no un rm al final: si el usuario corta con Ctrl-C, el temporal se
# borra igual.
trap 'rm -f "$OUT"' EXIT

"${DC[@]}" exec -T "${PYTEST_ENV[@]}" web pytest -q "${PYTEST_ARGS[@]}" 2>&1 | tee "$OUT"
STATUS=${PIPESTATUS[0]}

# --- 5. Resumen -------------------------------------------------------------
# Se relee la línea de resumen de pytest en vez de recontar: es la fuente de
# verdad y ya distingue passed/failed/error/skipped.
RESUMEN="$(grep -E '^(=+ )?[0-9]+ (passed|failed|error)' "$OUT" | tail -1)"
[[ -n "$RESUMEN" ]] || RESUMEN="$(tail -1 "$OUT")"

extraer() { grep -oE "[0-9]+ $1" <<< "$RESUMEN" | grep -oE '^[0-9]+' || true; }
PASSED="$(extraer passed)";  FAILED="$(extraer failed)"
SKIPPED="$(extraer skipped)"; ERRORS="$(extraer 'error(s)?')"

printf "\n${C_BOLD}Resumen${C_OFF}\n"
printf "  ${C_OK}passed${C_OFF}  %s\n" "${PASSED:-0}"
printf "  ${C_ERR}failed${C_OFF}  %s\n" "${FAILED:-0}"
printf "  ${C_ERR}errors${C_OFF}  %s\n" "${ERRORS:-0}"
printf "  ${C_WARN}skipped${C_OFF} %s   (un SKIP no es un PASS: eso no se ha verificado)\n" "${SKIPPED:-0}"
printf "  motor   %s\n" "$MOTOR"

echo
if [[ $STATUS -eq 0 ]]; then
  ok "la suite pasó"
else
  bad "la suite falló (pytest salió con $STATUS)"
  printf "      Busca las líneas 'FAILED' más arriba para el detalle.\n"
fi

# El stack se deja levantado a propósito: es lo que quiere quien acaba de
# correr los tests y va a seguir trabajando. Se para con `./dev.sh stop`.
exit $STATUS
