#!/usr/bin/env bash
# ============================================================================
# Plataforma Delphos — arranque de entorno de desarrollo
# ----------------------------------------------------------------------------
# Levanta backend (PostgreSQL + API en Docker) y frontend (Vite) de una vez.
#
#   ./dev.sh          arranca todo y espera a que responda
#   ./dev.sh stop     detiene todo (los datos de Postgres se conservan)
#   ./dev.sh restart  stop + start
#   ./dev.sh status   estado de los tres servicios
#   ./dev.sh logs     logs de la API (Ctrl-C para salir)
#   ./dev.sh logs web|db|front
# ============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
RUNDIR="$ROOT/.dev"
FRONT_LOG="$RUNDIR/frontend.log"
FRONT_PID="$RUNDIR/frontend.pid"

API_URL="http://localhost:8000"
FRONT_PORT=5173
FRONT_URL="http://localhost:$FRONT_PORT"

mkdir -p "$RUNDIR"

say()  { printf '\033[36m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m  ✓\033[0m %s\n' "$*"; }
warn() { printf '\033[33m  !\033[0m %s\n' "$*"; }
die()  { printf '\033[31m  ✗\033[0m %s\n' "$*" >&2; exit 1; }

front_running() {
  [[ -f "$FRONT_PID" ]] && kill -0 "$(cat "$FRONT_PID")" 2>/dev/null
}

# --- backend ---------------------------------------------------------------

start_backend() {
  command -v docker >/dev/null || die "docker no está instalado"
  docker info >/dev/null 2>&1 || die "el daemon de Docker no está corriendo"

  say "Backend: PostgreSQL + API (Docker)"
  docker compose -f "$BACKEND/docker-compose.yml" up -d --build db web

  # Se espera contra "/" a propósito: basta con que el proceso atienda, y así
  # este bucle no depende del HEALTHCHECK del contenedor.
  # (La ruta /health existe desde 17e8cd3 y responde 200; el contenedor sí
  # figura como "healthy". Antes no era así y aquí había un aviso al respecto.)
  printf '  esperando a la API'
  for _ in $(seq 1 60); do
    if curl -fsS -m 2 "$API_URL/" >/dev/null 2>&1; then
      echo; ok "API viva en $API_URL  (docs: $API_URL/docs)"
      return 0
    fi
    printf '.'; sleep 1
  done
  echo
  die "la API no respondió en 60s — revisa: ./dev.sh logs web"
}

# --- frontend --------------------------------------------------------------

start_frontend() {
  say "Frontend: Vite"

  if front_running; then
    ok "ya estaba corriendo (pid $(cat "$FRONT_PID")) en $FRONT_URL"
    return 0
  fi

  if [[ ! -d "$FRONTEND/node_modules" ]]; then
    say "node_modules ausente, instalando dependencias"
    if command -v npm >/dev/null; then
      (cd "$FRONTEND" && npm install)
    elif command -v yarn >/dev/null; then
      warn "npm no encontrado, usando yarn (no commitees el yarn.lock que genere)"
      (cd "$FRONTEND" && yarn install)
    else
      die "hace falta npm o yarn para instalar el frontend"
    fi
  fi

  [[ -x "$FRONTEND/node_modules/.bin/vite" ]] || die "vite no está en node_modules"

  # Se invoca el binario directamente: no depende de que npm esté en el PATH.
  # setsid + stdin cerrado: Vite queda en su propia sesión, sin heredar la
  # terminal ni la salida del script (si no, este no termina nunca).
  cd "$FRONTEND"
  setsid ./node_modules/.bin/vite --port "$FRONT_PORT" \
      </dev/null >"$FRONT_LOG" 2>&1 &
  echo $! >"$FRONT_PID"
  cd "$ROOT"
  disown 2>/dev/null || true

  printf '  esperando a Vite'
  for _ in $(seq 1 30); do
    if curl -fsS -m 2 "$FRONT_URL/" >/dev/null 2>&1; then
      echo; ok "frontend en $FRONT_URL  (log: $FRONT_LOG)"
      return 0
    fi
    front_running || { echo; cat "$FRONT_LOG"; die "Vite murió al arrancar"; }
    printf '.'; sleep 1
  done
  echo
  cat "$FRONT_LOG"
  die "Vite no respondió en 30s"
}

stop_frontend() {
  if front_running; then
    kill "$(cat "$FRONT_PID")" 2>/dev/null || true
    sleep 1
    kill -0 "$(cat "$FRONT_PID")" 2>/dev/null && kill -9 "$(cat "$FRONT_PID")" 2>/dev/null || true
    ok "frontend detenido"
  else
    ok "frontend no estaba corriendo"
  fi
  rm -f "$FRONT_PID"
}

# --- comandos --------------------------------------------------------------

cmd_start() {
  start_backend
  start_frontend
  echo
  printf '\033[32mListo.\033[0m  Frontend %s  ·  API %s  ·  Docs %s/docs\n' \
    "$FRONT_URL" "$API_URL" "$API_URL"
  echo "Parar todo con: ./dev.sh stop"
}

cmd_stop() {
  say "Deteniendo"
  stop_frontend
  docker compose -f "$BACKEND/docker-compose.yml" down
  ok "backend detenido (los datos de Postgres se conservan; usa 'down -v' para borrarlos)"
}

cmd_status() {
  docker compose -f "$BACKEND/docker-compose.yml" ps
  echo
  if front_running; then
    ok "frontend corriendo (pid $(cat "$FRONT_PID")) → $FRONT_URL"
  else
    warn "frontend parado"
  fi
}

cmd_logs() {
  case "${1:-web}" in
    front|frontend) tail -f "$FRONT_LOG" ;;
    web|db)         docker compose -f "$BACKEND/docker-compose.yml" logs -f "$1" ;;
    *)              die "logs: usa web | db | front" ;;
  esac
}

case "${1:-start}" in
  start)   cmd_start ;;
  stop)    cmd_stop ;;
  restart) cmd_stop; echo; cmd_start ;;
  status)  cmd_status ;;
  logs)    shift; cmd_logs "$@" ;;
  *)       die "uso: ./dev.sh [start|stop|restart|status|logs [web|db|front]]" ;;
esac
