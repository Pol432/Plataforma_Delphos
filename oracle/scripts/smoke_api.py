#!/usr/bin/env python3
"""
Smoke test de los endpoints `/api/v1/oracle/*` del backend.

Sólo usa la librería estándar: no hace falta venv ni instalar nada. Está
pensado para Alex y Matías, que consumen el oráculo por HTTP y no necesitan
montar los entornos de Python de `oracle/`.

    python3 oracle/scripts/smoke_api.py
    python3 oracle/scripts/smoke_api.py --api-url http://localhost:8000
    python3 oracle/scripts/smoke_api.py --no-fallback   # sin tocar Docker

Cada comprobación imprime PASS o FAIL con lo que esperaba y lo que encontró,
así que un fallo se localiza sin leer el código. Salida: 0 si todo pasa, 1 si
algo falla. Un SKIP no hace fallar el script pero **no es un PASS**.

La última sección apaga el modelo con el kill switch (`ORACLE_ENGINE`) para
comprobar que la respuesta cae al heurístico, y lo vuelve a encender. Eso
reinicia el contenedor `web` dos veces y necesita Docker; con `--no-fallback`
se salta. Pase lo que pase, el estado se restaura antes de salir.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

# Usuario fijo de pruebas: si ya existe, el registro devuelve 400 y seguimos.
# Es idempotente a propósito — no se borra al terminar porque el endpoint de
# borrado de usuarios no existe, y dejar basura distinta en cada ejecución
# sería peor que dejar siempre la misma. El nombre lo delata como artefacto.
TEST_USER = "oracle_smoke"
TEST_EMAIL = "oracle_smoke@test.dev"
TEST_PASSWORD = "Demo12345!"

# --- Estado esperado del subsistema -----------------------------------------
# Estos números son el contrato que verifica el script. Si cambian a
# propósito (se añade una simulación, crece el vocabulario), hay que
# actualizarlos aquí: que el script falle ante un cambio no anunciado es
# justamente lo que se quiere.
N_SKILLS = 70
N_SIMULACIONES = 64

# El grupo de alias más usado como ejemplo: un canónico y dos alias que
# comparten su skill_id. Es lo que `canonical_name` vino a hacer distinguible.
ALIAS_GROUP_ID = 39
ALIAS_GROUP_CANONICAL = "Adobe Creative Suite"
ALIAS_GROUP_SIZE = 3  # 1 canónico + 2 alias

# Perfil de la regresión de OOV: estas dos simulaciones se quedaban con
# `matched_skills` vacío porque los alias no se resolvían contra el catálogo.
OOV_PROFILE = {
    "skills": [
        "Figma", "Adobe Creative Suite", "Project Management",
        "Agile", "Communication", "Leadership", "Prototyping", "User Research",
    ],
    "field_of_study": "Design",
    "top_n": 64,
}
OOV_SIMULACIONES = ("sim_ux_designer", "sim_project_manager")

GREEN, RED, YELLOW, CYAN, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[1m", "\033[0m",
)

# (nombre, estado, detalle) con estado en {"PASS", "FAIL", "SKIP"}.
_results: list[tuple[str, str, str]] = []


def check(name: str, condition: bool, detail: str = "") -> bool:
    """Registra e imprime una comprobación. `detail` debe decir qué se encontró."""
    _results.append((name, "PASS" if condition else "FAIL", detail))
    mark = f"{GREEN}PASS{RESET}" if condition else f"{RED}FAIL{RESET}"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    return condition


def skip(name: str, motivo: str) -> None:
    """Algo que no se ha podido verificar. No hace fallar, pero no es un PASS."""
    _results.append((name, "SKIP", motivo))
    print(f"  [{YELLOW}SKIP{RESET}] {name} — {motivo}")


def section(title: str) -> None:
    print(f"\n{BOLD}{title}{RESET}")


def request(
    url: str,
    *,
    method: str = "GET",
    token: str | None = None,
    json_body: dict | None = None,
    form_body: dict | None = None,
) -> tuple[int, object]:
    """Devuelve (status, body_parseado). No lanza excepción en 4xx/5xx."""
    data = None
    headers = {"Accept": "application/json"}

    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"
    elif form_body is not None:
        data = urllib.parse.urlencode(form_body).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw, status = resp.read(), resp.status
    except urllib.error.HTTPError as exc:
        raw, status = exc.read(), exc.code
    except urllib.error.URLError as exc:
        raise SystemExit(
            f"{RED}No se pudo conectar con {url}{RESET}\n"
            f"  {exc.reason}\n"
            f"  ¿Está el backend levantado? Prueba: ./dev.sh status"
        )

    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, raw.decode(errors="replace")


def login(api: str) -> str:
    """Registra (si hace falta) y devuelve un token."""
    section("0 · Autenticación")

    status, _ = request(
        f"{api}/api/v1/register",
        method="POST",
        json_body={
            "username": TEST_USER,
            "email": TEST_EMAIL,
            "full_name": "Oracle Smoke",
            "password": TEST_PASSWORD,
        },
    )
    # 201 = creado ahora; 400 = ya existía de una ejecución anterior.
    check(
        "registro del usuario de pruebas",
        status in (201, 400),
        "ya existía" if status == 400 else f"creado (HTTP {status})",
    )

    status, body = request(
        f"{api}/api/v1/token",
        method="POST",
        form_body={"username": TEST_USER, "password": TEST_PASSWORD},
    )
    token = body.get("access_token", "") if isinstance(body, dict) else ""
    if not check("login devuelve access_token", status == 200 and bool(token),
                 f"HTTP {status}"):
        raise SystemExit(
            f"\n{RED}Sin token no se puede seguir: los 4 endpoints "
            f"del oráculo exigen autenticación.{RESET}"
        )
    return token


def test_auth_required(api: str) -> None:
    section("1 · Los endpoints exigen autenticación")
    for path in ("catalog", "skills"):
        status, _ = request(f"{api}/api/v1/oracle/{path}")
        check(f"GET /{path} sin token es rechazado", status in (401, 403),
              f"HTTP {status}")


def test_catalog(api: str, token: str) -> None:
    section("2 · GET /oracle/catalog")
    status, body = request(f"{api}/api/v1/oracle/catalog", token=token)
    if not check("responde 200", status == 200, f"HTTP {status}"):
        return

    sims = body.get("simulations", []) if isinstance(body, dict) else []
    check(f"trae {N_SIMULACIONES} simulaciones", len(sims) == N_SIMULACIONES,
          f"esperado {N_SIMULACIONES}, encontrado {len(sims)}")
    check("`count` concuerda con la lista", body.get("count") == len(sims),
          f"count={body.get('count')} vs len={len(sims)}")
    check("declara el tamaño del vocabulario de skills",
          isinstance(body.get("skill_vocabulary_size"), int),
          f"{body.get('skill_vocabulary_size')} entradas")

    if sims:
        campos = {"simulation_id", "title", "base_career", "categoria",
                  "nivel_dificultad", "duracion_horas"}
        faltan = campos - set(sims[0])
        check("cada simulación trae los campos esperados", not faltan,
              f"faltan: {sorted(faltan)}" if faltan else "")


def test_skills(api: str, token: str) -> None:
    section("3 · GET /oracle/skills")
    status, body = request(f"{api}/api/v1/oracle/skills", token=token)
    if not check("responde 200", status == 200, f"HTTP {status}"):
        return

    entries = body if isinstance(body, list) else body.get("skills", [])
    check(f"trae {N_SKILLS} entradas", len(entries) == N_SKILLS,
          f"esperado {N_SKILLS}, encontrado {len(entries)}")
    if not entries:
        return

    # `canonical_name` es lo que permite distinguir un alias de un skill
    # entrenado: skill_id no sirve porque los alias comparten el ID de su
    # equivalente (ver el docstring del endpoint).
    sin_canonical = [e.get("name") for e in entries if "canonical_name" not in e]
    tiene_canonical = check(
        "toda entrada trae `canonical_name`", not sin_canonical,
        f"{len(sin_canonical)} sin él: {sin_canonical[:5]}" if sin_canonical
        else f"las {len(entries)} entradas lo traen",
    )
    if not tiene_canonical:
        return

    alias = [e for e in entries if e.get("name") != e.get("canonical_name")]
    check("la regla de alias (name != canonical_name) discrimina",
          len(alias) > 0,
          f"{len(alias)} alias sobre {len(entries)} entradas")

    # El grupo de ejemplo: mismo skill_id, un canónico y dos alias apuntándole.
    grupo = [e for e in entries if e.get("skill_id") == ALIAS_GROUP_ID]
    nombres = sorted(e.get("name") for e in grupo)
    if not check(f"el grupo id={ALIAS_GROUP_ID} tiene {ALIAS_GROUP_SIZE} entradas",
                 len(grupo) == ALIAS_GROUP_SIZE,
                 f"esperado {ALIAS_GROUP_SIZE}, encontrado {len(grupo)}: {nombres}"):
        return

    canonicos = [e for e in grupo if e.get("name") == e.get("canonical_name")]
    check(f"el grupo id={ALIAS_GROUP_ID} tiene un único canónico",
          len(canonicos) == 1
          and canonicos[0].get("name") == ALIAS_GROUP_CANONICAL,
          f"esperado 1 × {ALIAS_GROUP_CANONICAL!r}, encontrado "
          f"{[e.get('name') for e in canonicos]}")

    apuntan_bien = [e for e in grupo
                    if e.get("canonical_name") == ALIAS_GROUP_CANONICAL]
    check(f"los {ALIAS_GROUP_SIZE - 1} alias del grupo apuntan al canónico",
          len(apuntan_bien) == ALIAS_GROUP_SIZE,
          f"esperado que las {ALIAS_GROUP_SIZE} entradas resuelvan a "
          f"{ALIAS_GROUP_CANONICAL!r}, lo hacen {len(apuntan_bien)}: {nombres}")


def test_recommend(api: str, token: str) -> None:
    section("4 · POST /oracle/recommend")
    payload = {
        "skills": ["Python", "Figma"],
        "field_of_study": "Computer Science",
        "top_n": 3,
    }
    status, body = request(f"{api}/api/v1/oracle/recommend", method="POST",
                           token=token, json_body=payload)
    if not check("responde 200", status == 200, f"HTTP {status}"):
        return

    recs = body.get("recommendations", [])
    check("respeta top_n", len(recs) == payload["top_n"],
          f"pidió {payload['top_n']}, devolvió {len(recs)}")
    check("resuelve los skills enviados",
          len(body.get("resolved_skill_ids", [])) == 2,
          f"resueltos={body.get('resolved_skill_ids')} "
          f"sin resolver={body.get('unresolved_skills')}")

    # --- Procedencia de los números -----------------------------------------
    # El punto delicado documentado en el README raíz: aunque `engine` diga
    # "wide_and_deep", el modelo sólo decide el ORDEN. Todos los valores de
    # `scores` los calcula el heurístico. Se comprueba explícitamente para que
    # nadie presente esos números como salida del modelo entrenado.
    #
    # Aquí se exige el estado sano (modelo cargado). Si el modelo se cayó, la
    # API responde igual pero con heuristic_bridge_v1 en los tres campos: eso
    # es un fallback correcto, y el script debe cantarlo como FAIL porque no
    # es el estado esperado en una máquina sana.
    engine_ok = check(
        "`engine` es wide_and_deep (el modelo está cargado)",
        body.get("engine") == "wide_and_deep",
        f"esperado 'wide_and_deep', encontrado {body.get('engine')!r}",
    )
    if not engine_ok and body.get("engine") == "heuristic_bridge_v1":
        print(f"      {YELLOW}El modelo no está ordenando: se ha caído al "
              f"heurístico.{RESET}")
        print(f"      Mira el log: docker compose -f backend/docker-compose.yml "
              f"logs web | grep -i wide")
        print(f"      Y comprueba que ORACLE_ENGINE valga 'auto'.")

    check("declara quién puntúa (`scored_by`)",
          body.get("scored_by") == "heuristic_bridge_v1",
          f"esperado 'heuristic_bridge_v1', encontrado {body.get('scored_by')!r}")
    check("declara quién ordena (`ranked_by`)",
          body.get("ranked_by") == "wide_and_deep",
          f"esperado 'wide_and_deep', encontrado {body.get('ranked_by')!r}")

    if not recs:
        return

    esperados = {"engagement_probability", "skill_overlap_score",
                 "difficulty_match_score", "confidence_interval"}
    incompletos = [r["simulation_id"] for r in recs
                   if esperados - set(r.get("scores", {}))]
    check("cada item trae el bloque `scores` completo", not incompletos,
          f"incompletos: {incompletos}" if incompletos
          else f"los {len(recs)} items")

    # No es una estimación de incertidumbre; hoy se publica en null. Se mira
    # item por item, no sólo el primero: fabricarlo en uno solo ya sería un bug.
    con_ci = [(r["simulation_id"], r["scores"]["confidence_interval"])
              for r in recs if r.get("scores", {}).get("confidence_interval")
              is not None]
    check("`confidence_interval` es null en TODOS los items (no se fabrica)",
          not con_ci,
          f"esperado null en {len(recs)}, con valor: {con_ci}" if con_ci
          else f"null en los {len(recs)} items")

    # --- Prueba de que el modelo reordena de verdad --------------------------
    # Si `ranked_by` dice wide_and_deep pero la lista sale ordenada por
    # engagement_probability descendente, el modelo podría no estar haciendo
    # nada: sería indistinguible de devolver el orden del heurístico. Que NO
    # esté ordenada es la evidencia de que hay una permutación real encima.
    #
    # Se pide el catálogo entero para esto, y no los 3 de arriba: con 3 items
    # salir en orden decreciente por casualidad tiene 1 probabilidad entre 6
    # aunque el modelo esté reordenando de verdad. Sobre 64 la coincidencia
    # deja de ser plausible y el check pasa a significar algo.
    status, full = request(
        f"{api}/api/v1/oracle/recommend", method="POST", token=token,
        json_body={**payload, "top_n": N_SIMULACIONES},
    )
    if not check(f"acepta top_n={N_SIMULACIONES} (catálogo completo)",
                 status == 200, f"HTTP {status}"):
        return

    todas = full.get("recommendations", [])
    orden = [r["scores"]["engagement_probability"] for r in todas]
    if full.get("ranked_by") == "wide_and_deep":
        # Se informa de cuántas posiciones se salen del orden heurístico: un
        # "no está ordenado" a secas no dice si el modelo mueve mucho o poco.
        desorden = sum(1 for a, b in zip(orden, sorted(orden, reverse=True))
                       if a != b)
        check("el orden NO es el de engagement_probability (el modelo reordena)",
              orden != sorted(orden, reverse=True),
              f"{desorden}/{len(orden)} posiciones difieren del orden heurístico"
              if desorden else
              f"la lista de {len(orden)} coincide con el orden heurístico: "
              f"el modelo no está reordenando nada")
    else:
        # Ordenando el heurístico, sus propios scores sí deben ir decrecientes.
        check("ordenado por probabilidad heurística descendente",
              orden == sorted(orden, reverse=True), f"{orden}")


def test_recommend_validation(api: str, token: str) -> None:
    section("5 · POST /oracle/recommend — validación de entrada")
    # top_n está acotado a 1..64 en el esquema.
    status, _ = request(f"{api}/api/v1/oracle/recommend", method="POST",
                        token=token, json_body={"skills": ["Python"], "top_n": 999})
    check("top_n fuera de rango devuelve 422", status == 422, f"HTTP {status}")

    status, body = request(f"{api}/api/v1/oracle/recommend", method="POST",
                           token=token,
                           json_body={"skills": ["NoExisteEsteSkill_xyz"]})
    if check("un skill desconocido no rompe la petición", status == 200,
             f"HTTP {status}"):
        check("y se reporta en `unresolved_skills`",
              "NoExisteEsteSkill_xyz" in body.get("unresolved_skills", []),
              f"{body.get('unresolved_skills')}")


def test_full_profile(api: str, token: str) -> None:
    section("6 · POST /oracle/full_profile")
    status, body = request(
        f"{api}/api/v1/oracle/full_profile", method="POST", token=token,
        json_body={"skills": ["Python", "SQL", "Figma"],
                   "field_of_study": "Computer Science", "top_n": 5},
    )
    if not check("responde 200", status == 200, f"HTTP {status}"):
        return

    # A diferencia de /recommend, este endpoint NO pasa por el Wide&Deep: los
    # tres campos declaran el heurístico. No es un fallo, es su diseño actual.
    for campo in ("engine", "scored_by", "ranked_by"):
        check(f"`{campo}` es heuristic_bridge_v1",
              body.get(campo) == "heuristic_bridge_v1",
              f"esperado 'heuristic_bridge_v1', encontrado {body.get(campo)!r}")

    recs = body.get("recommendations", [])
    con_ci = [r["simulation_id"] for r in recs
              if r.get("scores", {}).get("confidence_interval") is not None]
    check("`confidence_interval` es null en todos los items", not con_ci,
          f"con valor: {con_ci}" if con_ci else f"null en los {len(recs)} items")

    # El optimizador de rutas todavía no está enchufado, así que se espera una
    # lista vacía. Lo que se verifica es que el CAMPO exista y no reviente:
    # el día que se enchufe, el contrato del cliente ya no cambia.
    presente = check("el campo `learning_paths` existe", "learning_paths" in body,
                     f"claves: {sorted(body)}")
    if presente:
        lp = body.get("learning_paths")
        check("`learning_paths` es una lista", isinstance(lp, list),
              f"tipo={type(lp).__name__}, valor={lp!r} "
              f"(hoy se espera [], el optimizador aún no está enchufado)")


def test_oov_mapping(api: str, token: str) -> None:
    """
    Regresión del bug de `matched_skills` vacío.

    Los alias del perfil (Figma → Adobe Creative Suite, etc.) no se resolvían
    contra el catálogo, así que estas dos simulaciones salían recomendadas
    pero sin ninguna skill que justificara por qué. Si `matched_skills` vuelve
    a salir vacío aquí, el mapeo OOV se ha roto otra vez.
    """
    section("7 · Mapeo OOV — `matched_skills` no vuelve a salir vacío")
    status, body = request(f"{api}/api/v1/oracle/recommend", method="POST",
                           token=token, json_body=OOV_PROFILE)
    if not check("responde 200", status == 200, f"HTTP {status}"):
        return

    por_id = {r["simulation_id"]: r for r in body.get("recommendations", [])}
    for sim in OOV_SIMULACIONES:
        rec = por_id.get(sim)
        if rec is None:
            check(f"{sim} aparece en la respuesta", False,
                  f"no está entre las {len(por_id)} simulaciones devueltas")
            continue
        matched = rec.get("matched_skills") or []
        check(f"{sim} trae `matched_skills` no vacío", bool(matched),
              f"encontrado {matched}" if matched
              else "encontrado [] — la regresión de OOV ha vuelto")


# ---------------------------------------------------------------------------
# Fallback: apagar el modelo y comprobar que la API no se rompe
# ---------------------------------------------------------------------------

# `ORACLE_ENGINE` está fijado a `auto` en el compose, no leído del entorno del
# host, así que no basta con exportar la variable: hay que recrear el servicio
# con un override. Se escribe en un temporal y se borra siempre.
_OVERRIDE = "services:\n  web:\n    environment:\n      ORACLE_ENGINE: heuristic\n"


def _compose_base(root: str) -> list[str]:
    return ["docker", "compose", "-f", os.path.join(root, "backend",
                                                    "docker-compose.yml")]


def _esperar_api(api: str, segundos: int = 90) -> bool:
    """Espera a que la API vuelva a responder tras recrear el contenedor."""
    limite = time.time() + segundos
    while time.time() < limite:
        try:
            with urllib.request.urlopen(f"{api}/health", timeout=3) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def _engine_actual(api: str, token: str) -> object:
    _, body = request(f"{api}/api/v1/oracle/recommend", method="POST",
                      token=token, json_body={"skills": ["Python", "Figma"],
                                              "top_n": 3})
    return body.get("engine") if isinstance(body, dict) else None


def test_fallback(api: str, token: str, root: str) -> None:
    section("8 · Fallback — el kill switch no rompe la API")

    if subprocess.run(["docker", "info"], capture_output=True).returncode != 0:
        skip("fallback al heurístico",
             "Docker no responde; hace falta para mover ORACLE_ENGINE")
        skip("recuperación al estado normal", "depende de la anterior")
        return

    dc = _compose_base(root)
    tmp = tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False)
    tmp.write(_OVERRIDE)
    tmp.close()

    # El finally es lo importante: pase lo que pase (fallo, Ctrl-C, excepción)
    # el contenedor se recrea sin el override. Nadie debe encontrarse el stack
    # con el modelo apagado por culpa de este script.
    try:
        print(f"  {CYAN}·{RESET} recreando `web` con ORACLE_ENGINE=heuristic "
              f"(tarda unos segundos)")
        recreado = subprocess.run(
            dc + ["-f", tmp.name, "up", "-d", "web"], capture_output=True)
        if recreado.returncode != 0 or not _esperar_api(api):
            check("fallback al heurístico", False,
                  "no se pudo recrear el contenedor con el kill switch")
            return

        engine = _engine_actual(api, token)
        check("con el modelo apagado, `engine` cae a heuristic_bridge_v1",
              engine == "heuristic_bridge_v1",
              f"esperado 'heuristic_bridge_v1', encontrado {engine!r}")
    finally:
        print(f"  {CYAN}·{RESET} restaurando ORACLE_ENGINE=auto")
        subprocess.run(dc + ["up", "-d", "web"], capture_output=True)
        os.unlink(tmp.name)

    if not _esperar_api(api):
        check("la API vuelve tras restaurar", False,
              "el contenedor no respondió a /health en 90 s")
        return

    engine = _engine_actual(api, token)
    check("tras restaurar, `engine` vuelve a wide_and_deep",
          engine == "wide_and_deep",
          f"esperado 'wide_and_deep', encontrado {engine!r}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test de los endpoints /api/v1/oracle/*.")
    parser.add_argument("--api-url", default="http://localhost:8000",
                        help="URL base de la API (por defecto http://localhost:8000)")
    parser.add_argument("--no-fallback", action="store_true",
                        help="salta la sección 8, que reinicia el contenedor web")
    args = parser.parse_args()
    api = args.api_url.rstrip("/")
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))

    print(f"{BOLD}Smoke test · endpoints /api/v1/oracle/*{RESET}")
    print(f"API: {api}")

    token = login(api)
    test_auth_required(api)
    test_catalog(api, token)
    test_skills(api, token)
    test_recommend(api, token)
    test_recommend_validation(api, token)
    test_full_profile(api, token)
    test_oov_mapping(api, token)
    if args.no_fallback:
        section("8 · Fallback — el kill switch no rompe la API")
        skip("fallback al heurístico", "--no-fallback")
        skip("recuperación al estado normal", "--no-fallback")
    else:
        test_fallback(api, token, root)

    fallos = [r for r in _results if r[1] == "FAIL"]
    saltadas = [r for r in _results if r[1] == "SKIP"]
    pasadas = [r for r in _results if r[1] == "PASS"]
    # Las saltadas no cuentan en el denominador: no se han verificado, así que
    # no son ni éxito ni fracaso. Se listan aparte para que no se confundan.
    total = len(pasadas) + len(fallos)

    print(f"\n{BOLD}Resumen{RESET}")
    if saltadas:
        print(f"  {YELLOW}{len(saltadas)} saltadas{RESET} "
              f"(un SKIP no es un PASS):")
        for name, _, detail in saltadas:
            print(f"    - {name} — {detail}")

    if fallos:
        print(f"  {RED}{BOLD}{len(pasadas)}/{total} comprobaciones pasaron — "
              f"{len(fallos)} fallaron:{RESET}")
        for name, _, detail in fallos:
            print(f"    {RED}FAIL{RESET} {name}" + (f" — {detail}" if detail else ""))
        return 1

    print(f"  {GREEN}{BOLD}{len(pasadas)}/{total} comprobaciones pasaron.{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
