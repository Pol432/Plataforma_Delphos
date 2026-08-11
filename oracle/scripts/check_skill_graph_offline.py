#!/usr/bin/env python3
"""
Comprobaciones de `skill_graph` que NO necesitan base de datos ni MindSpore.

El end-to-end de skill_graph exige PostgreSQL, MindSpore y un checkpoint que
no existe en el repo, así que en la mayoría de máquinas se salta entero. Este
script cubre la parte que sí es verificable en cualquier sitio: la inferencia
por texto (regex pura) y el cuestionario de onboarding.

Lo que NO se puede comprobar aquí, y por qué:

  · `skill_taxonomy` — llama a `load_skill_catalog()` en tiempo de import, es
    decir consulta `habilidades_catalogo` en PostgreSQL. Sin base de datos no
    es importable siquiera, así que no hay forma de validarla en frío.
  · `inference.mindspore_model` — importa MindSpore, que no tiene wheels para
    Python 3.12+.

Uso:  python3 oracle/scripts/check_skill_graph_offline.py
Sale 0 si todo pasa, 1 si algo falla.
"""

from __future__ import annotations

import sys
from pathlib import Path

# El paquete asume que su raíz está en sys.path (lo hace config.py en runtime).
SKILL_GRAPH = Path(__file__).resolve().parents[1] / "skill_graph"
sys.path.insert(0, str(SKILL_GRAPH))

GREEN, RED, RESET, BOLD = "\033[32m", "\033[31m", "\033[0m", "\033[1m"

_failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> bool:
    mark = f"{GREEN}✓{RESET}" if condition else f"{RED}✗{RESET}"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))
    if not condition:
        _failures.append(name)
    return condition


def test_text_inference() -> None:
    print(f"\n{BOLD}Inferencia por texto (regex, sin dependencias){RESET}")
    try:
        from inference.text_inference import (
            SKILL_KEYWORDS,
            extract_skills_from_text,
            infer_implicit_skills,
        )
    except Exception as exc:  # noqa: BLE001
        check("importa inference.text_inference", False, repr(exc))
        return

    check("el diccionario de keywords no está vacío",
          len(SKILL_KEYWORDS) > 0, f"{len(SKILL_KEYWORDS)} skills con keywords")

    texto = "Implemented a REST API in Python with Docker and SQL queries."
    hallados = extract_skills_from_text(texto)
    check("extrae skills de un texto de ejemplo",
          len(hallados) > 0, f"{sorted(hallados)}")
    esperados = {"python", "sql", "docker", "rest_api"}
    faltan = esperados - set(hallados)
    check("reconoce los skills evidentes del texto", not faltan,
          f"no detectó: {sorted(faltan)}" if faltan else "python, sql, docker, rest_api")

    check("las puntuaciones son numéricas y positivas",
          all(isinstance(v, (int, float)) and v > 0 for v in hallados.values()),
          f"{hallados}")

    vacio = extract_skills_from_text("")
    check("un texto vacío no inventa skills", len(vacio) == 0, f"{vacio}")

    implicitos = infer_implicit_skills(hallados)
    check("deriva skills implícitos de los explícitos",
          len(implicitos) > 0, f"{len(implicitos)} implícitos")
    # Los implícitos son transversales (pensamiento analítico y compañía); no
    # deben limitarse a repetir lo que ya venía explícito.
    check("los implícitos aportan algo nuevo",
          bool(set(implicitos) - set(hallados)),
          f"{sorted(set(implicitos) - set(hallados))[:4]}")


def test_onboarding_quiz() -> None:
    print(f"\n{BOLD}Cuestionario de onboarding{RESET}")
    try:
        from inference.onboarding_quiz import (
            get_all_questions,
            get_question,
            score_quiz,
        )
    except Exception as exc:  # noqa: BLE001
        check("importa inference.onboarding_quiz", False, repr(exc))
        return

    preguntas = get_all_questions()
    check("hay preguntas cargadas", len(preguntas) > 0, f"{len(preguntas)} preguntas")
    if not preguntas:
        return

    bien_formadas = all(
        q.get("id") and q.get("question") and q.get("opciones")
        for q in preguntas
    )
    check("toda pregunta trae id, enunciado y opciones", bien_formadas)

    ids = [q["id"] for q in preguntas]
    check("los ids de pregunta no se repiten", len(set(ids)) == len(ids))

    primera = get_question(ids[0])
    check("get_question recupera por id",
          primera is not None and primera.get("id") == ids[0])

    # Se responde a todo con la primera opción: sólo interesa que puntúe.
    respuestas = {q["id"]: q["opciones"][0]["id"] for q in preguntas}
    puntuacion = score_quiz(respuestas)
    check("score_quiz devuelve puntuaciones",
          len(puntuacion) > 0, f"{len(puntuacion)} skills puntuados")
    check("las puntuaciones son numéricas",
          all(isinstance(v, (int, float)) for v in puntuacion.values()))

    vacio = score_quiz({})
    check("un cuestionario sin respuestas no puntúa nada",
          len(vacio) == 0, f"{vacio}")


def test_migrations_present() -> None:
    print(f"\n{BOLD}Migraciones de base de datos{RESET}")
    migraciones = sorted((SKILL_GRAPH / "db" / "migrations").glob("*.sql"))
    check("existen ficheros de migración", len(migraciones) > 0,
          ", ".join(m.name for m in migraciones))
    check("ninguna migración está vacía",
          all(m.stat().st_size > 0 for m in migraciones))


def test_checkpoint_status() -> None:
    print(f"\n{BOLD}Estado del checkpoint{RESET}")
    ckpt = SKILL_GRAPH / "checkpoints" / "task_eval_model.ckpt"
    if ckpt.exists():
        check("task_eval_model.ckpt presente", True, f"{ckpt.stat().st_size} bytes")
    else:
        # No es un fallo del código: es una carencia conocida y documentada.
        # Se informa sin marcarlo como error para no enmascarar fallos reales.
        print(f"  {RED}·{RESET} task_eval_model.ckpt NO existe — el modelo cae a "
              f"pesos aleatorios")
        print("    Mientras falte, cualquier predicción de skill_graph es ruido.")
        print("    Ver oracle/skill_graph/README_CHECKPOINT_STATUS.md")


def main() -> int:
    print(f"{BOLD}skill_graph · comprobaciones sin base de datos{RESET}")
    test_text_inference()
    test_onboarding_quiz()
    test_migrations_present()
    test_checkpoint_status()

    print()
    if _failures:
        print(f"{RED}{BOLD}{len(_failures)} comprobaciones fallaron:{RESET}")
        for f in _failures:
            print(f"  {RED}✗{RESET} {f}")
        return 1
    print(f"{GREEN}{BOLD}Todas las comprobaciones offline pasaron.{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
