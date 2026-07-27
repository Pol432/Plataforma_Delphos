"""
inference/onboarding_quiz.py
----------------------------
15-question onboarding quiz that infers foundational skills
for any user — including high school students with zero tech experience.

Each question maps answers to skill scores (0–100 range).
Negative scores reduce a skill's initial estimate.
"""

from typing import Optional

# ── Quiz definition ────────────────────────────────────────────────────────

ONBOARDING_QUIZ: list[dict] = [
    {
        "id": "q1",
        "question": "Tienes que organizar un evento para tu colegio. ¿Por dónde empiezas?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Creo una lista de tareas con fechas límite para cada una"},
            {"id": "B", "texto": "Reúno a mis compañeros para generar ideas creativas"},
            {"id": "C", "texto": "Investigo cómo lo han hecho en otros colegios antes"},
            {"id": "D", "texto": "Empiezo a hacer los materiales visuales del evento"},
        ],
        "skill_mapping": {
            "A": {"planificacion_proyectos": 25, "gestion_tiempo": 20, "organizacion": 22, "gestion_cronograma": 18},
            "B": {"liderazgo": 20, "creatividad": 18, "comunicacion_verbal": 20, "trabajo_equipo": 22},
            "C": {"pensamiento_analitico": 25, "investigacion_mercado": 20, "resolucion_problemas": 18},
            "D": {"diseno_visual": 20, "creatividad": 22, "ideacion": 18, "diseno_grafico": 15},
        },
    },
    {
        "id": "q2",
        "question": "Tu profesor te da un problema de matemáticas que nunca has visto. ¿Qué haces primero?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Intento identificar patrones con problemas que ya conozco"},
            {"id": "B", "texto": "Lo divido en partes más pequeñas y ataco una por una"},
            {"id": "C", "texto": "Busco información o ejemplos similares para entender el contexto"},
            {"id": "D", "texto": "Le pregunto a alguien o trabajo con un compañero"},
        ],
        "skill_mapping": {
            "A": {"reconocimiento_patrones": 28, "razonamiento_abstracto": 22, "pensamiento_analitico": 20},
            "B": {"resolucion_problemas": 28, "razonamiento_logico": 25, "pensamiento_sistemico": 20},
            "C": {"investigacion_academica": 25, "velocidad_aprendizaje": 20, "revision_literatura": 18},
            "D": {"trabajo_equipo": 22, "escucha_activa": 20, "colaboracion": 25},
        },
    },
    {
        "id": "q3",
        "question": "Encuentras un error en un trabajo que ya entregaste. ¿Cómo reaccionas?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Lo analizo para entender por qué ocurrió y cómo evitarlo"},
            {"id": "B", "texto": "Lo corrijo de inmediato y sigo adelante sin darle más vueltas"},
            {"id": "C", "texto": "Me cuesta mucho, pero eventualmente lo acepto y aprendo"},
            {"id": "D", "texto": "Lo uso como motivación para mejorar en el futuro"},
        ],
        "skill_mapping": {
            "A": {"pensamiento_critico": 28, "atencion_al_detalle": 25, "autoevaluacion": 22},
            "B": {"resolucion_problemas": 20, "adaptabilidad": 25, "gestion_tiempo": 18},
            "C": {"resiliencia": 28, "inteligencia_emocional": 22, "manejo_estres": 20},
            "D": {"mentalidad_crecimiento": 30, "resiliencia": 22, "motivacion": 20},
        },
    },
    {
        "id": "q4",
        "question": "Te piden explicar un tema difícil a alguien que no sabe nada del área. ¿Cómo lo haces?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Uso analogías y ejemplos del día a día para que sea claro"},
            {"id": "B", "texto": "Hago un diagrama o visual para ilustrar las ideas"},
            {"id": "C", "texto": "Voy paso a paso desde lo más básico hasta lo complejo"},
            {"id": "D", "texto": "Le hago preguntas para entender qué sabe y adapto la explicación"},
        ],
        "skill_mapping": {
            "A": {"storytelling": 28, "comunicacion_verbal": 25, "comprension_conceptual": 20},
            "B": {"diseno_visual": 22, "visualizacion_datos": 20, "comunicacion_escrita": 18},
            "C": {"escritura_tecnica": 25, "pensamiento_sistemico": 22, "documentacion_tecnica": 20},
            "D": {"escucha_activa": 28, "empatia": 25, "investigacion_usuarios": 20},
        },
    },
    {
        "id": "q5",
        "question": "Tienes que completar un proyecto en 3 días pero el alcance es enorme. ¿Qué estrategia usas?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Listo todo, priorizo las tareas más críticas y delego el resto"},
            {"id": "B", "texto": "Reduzco el alcance a lo esencial y entrego algo funcional"},
            {"id": "C", "texto": "Trabajo intensamente sin dormir para terminarlo todo"},
            {"id": "D", "texto": "Negocio con quien me lo pidió para ajustar expectativas"},
        ],
        "skill_mapping": {
            "A": {"gestion_prioridades": 28, "delegacion": 22, "planificacion_proyectos": 25},
            "B": {"toma_decisiones": 28, "adaptabilidad": 22, "mejora_procesos": 18},
            "C": {"autodisciplina": 20, "resiliencia": 15, "manejo_estres": -10},
            "D": {"negociacion": 30, "comunicacion_verbal": 22, "gestion_stakeholders": 25},
        },
    },
    {
        "id": "q6",
        "question": "¿Cuál de estas actividades disfrutarías más en tu tiempo libre?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Resolver puzzles, acertijos o juegos de lógica"},
            {"id": "B", "texto": "Dibujar, diseñar o crear contenido visual"},
            {"id": "C", "texto": "Escribir: historias, artículos, o posts en redes sociales"},
            {"id": "D", "texto": "Organizar eventos o actividades para amigos o comunidad"},
        ],
        "skill_mapping": {
            "A": {"razonamiento_logico": 25, "pensamiento_analitico": 22, "reconocimiento_patrones": 20},
            "B": {"diseno_grafico": 28, "creatividad": 25, "diseno_visual": 22},
            "C": {"escritura_creativa": 28, "comunicacion_escrita": 25, "storytelling": 20},
            "D": {"liderazgo": 25, "organizacion": 22, "gestion_equipos": 20},
        },
    },
    {
        "id": "q7",
        "question": "Cuando trabajas en equipo y hay un conflicto de ideas, ¿qué rol tomas normalmente?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Mediar y buscar un punto intermedio que funcione para todos"},
            {"id": "B", "texto": "Defender mi idea si estoy convencido/a de que es la mejor"},
            {"id": "C", "texto": "Escuchar todas las perspectivas antes de dar mi opinión"},
            {"id": "D", "texto": "Proponer una prueba pequeña para ver qué idea funciona mejor"},
        ],
        "skill_mapping": {
            "A": {"resolucion_conflictos": 30, "negociacion": 22, "inteligencia_emocional": 25},
            "B": {"persuasion": 28, "comunicacion_verbal": 22, "pensamiento_critico": 20},
            "C": {"escucha_activa": 30, "empatia": 25, "toma_decisiones": 18},
            "D": {"pensamiento_analitico": 22, "ab_testing": 18, "innovacion": 20},
        },
    },
    {
        "id": "q8",
        "question": "Te dan un conjunto de datos con números y tendencias. ¿Qué haces con ellos?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Busco patrones y relaciones entre las variables"},
            {"id": "B", "texto": "Los visualizo en un gráfico para entenderlos mejor"},
            {"id": "C", "texto": "Me pierdo un poco, pero intento sacar conclusiones básicas"},
            {"id": "D", "texto": "Los uso para contar una historia sobre lo que significan"},
        ],
        "skill_mapping": {
            "A": {"analisis_datos": 28, "reconocimiento_patrones": 25, "estadistica": 20},
            "B": {"visualizacion_datos": 30, "pensamiento_analitico": 22, "diseno_visual": 15},
            "C": {"velocidad_aprendizaje": 15, "resolucion_problemas": 12},
            "D": {"storytelling": 25, "sintesis_informacion": 22, "comunicacion_escrita": 18},
        },
    },
    {
        "id": "q9",
        "question": "¿Cómo prefieres aprender algo completamente nuevo?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Leyendo documentación o teoría primero, luego practicando"},
            {"id": "B", "texto": "Saltando directo a hacer algo y aprendiendo sobre la marcha"},
            {"id": "C", "texto": "Viendo cómo lo hace alguien experto antes de intentarlo"},
            {"id": "D", "texto": "Tomando un curso estructurado de principio a fin"},
        ],
        "skill_mapping": {
            "A": {"investigacion_academica": 25, "comprension_conceptual": 22, "revision_literatura": 20},
            "B": {"adaptabilidad": 28, "resolucion_problemas": 22, "toma_riesgos": 20},
            "C": {"escucha_activa": 22, "velocidad_aprendizaje": 25, "atencion_al_detalle": 18},
            "D": {"organizacion": 22, "autodisciplina": 25, "planificacion_proyectos": 18},
        },
    },
    {
        "id": "q10",
        "question": "Tienes que presentar un proyecto ante personas que no conoces. ¿Cómo te preparas?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Preparo diapositivas visuales y practico varias veces"},
            {"id": "B", "texto": "Me enfoco en conocer bien a mi audiencia para adaptar el mensaje"},
            {"id": "C", "texto": "Escribo un guion completo y lo memorizo"},
            {"id": "D", "texto": "Prefiero improvisar — conozco el tema y eso es suficiente"},
        ],
        "skill_mapping": {
            "A": {"presentaciones": 30, "diseno_visual": 20, "comunicacion_verbal": 22},
            "B": {"investigacion_usuarios": 25, "empatia": 22, "adaptabilidad": 20},
            "C": {"escritura_tecnica": 22, "atencion_al_detalle": 20, "autodisciplina": 18},
            "D": {"comunicacion_verbal": 25, "confianza": 20, "adaptabilidad": 18},
        },
    },
    {
        "id": "q11",
        "question": "¿Qué tipo de problema te genera más satisfacción al resolver?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Un problema técnico complejo que requiere lógica precisa"},
            {"id": "B", "texto": "Un desafío creativo donde puedo expresar originalidad"},
            {"id": "C", "texto": "Un problema humano donde ayudo a alguien a mejorar su vida"},
            {"id": "D", "texto": "Un reto estratégico donde debo tomar decisiones con impacto"},
        ],
        "skill_mapping": {
            "A": {"razonamiento_logico": 28, "pensamiento_analitico": 25, "resolucion_problemas": 22},
            "B": {"creatividad": 30, "innovacion": 25, "ideacion": 22},
            "C": {"empatia": 30, "servicio_cliente": 22, "inteligencia_emocional": 25},
            "D": {"pensamiento_estrategico": 30, "toma_decisiones": 25, "liderazgo": 18},
        },
    },
    {
        "id": "q12",
        "question": "Cuando terminas una tarea, ¿qué es lo primero que haces?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "La reviso en detalle para asegurarme de que no hay errores"},
            {"id": "B", "texto": "La entrego y paso inmediatamente a lo siguiente"},
            {"id": "C", "texto": "Reflexiono sobre qué haría diferente la próxima vez"},
            {"id": "D", "texto": "La comparto para obtener retroalimentación"},
        ],
        "skill_mapping": {
            "A": {"atencion_al_detalle": 30, "aseguramiento_calidad": 25, "autoevaluacion": 20},
            "B": {"gestion_tiempo": 22, "orientacion_resultados": 25, "adaptabilidad": 15},
            "C": {"autoevaluacion": 28, "mentalidad_crecimiento": 25, "mejora_procesos": 22},
            "D": {"trabajo_equipo": 22, "comunicacion_verbal": 20, "colaboracion": 25},
        },
    },
    {
        "id": "q13",
        "question": "Si pudieras elegir un proyecto para el próximo mes, ¿cuál tomarías?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Construir una herramienta o sistema que automatice algo"},
            {"id": "B", "texto": "Diseñar la identidad visual de una marca desde cero"},
            {"id": "C", "texto": "Lanzar una campaña de contenido para un producto o causa"},
            {"id": "D", "texto": "Liderar un equipo para resolver un problema comunitario"},
        ],
        "skill_mapping": {
            "A": {"resolucion_problemas": 25, "pensamiento_sistemico": 22, "mejora_procesos": 20},
            "B": {"diseno_grafico": 30, "branding": 25, "diseno_visual": 22},
            "C": {"marketing": 28, "contenido_redes": 25, "copywriting": 22},
            "D": {"liderazgo": 30, "gestion_equipos": 25, "planificacion_proyectos": 20},
        },
    },
    {
        "id": "q14",
        "question": "Cuando recibes críticas sobre tu trabajo, ¿cómo reaccionas normalmente?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Las analizo objetivamente y decido cuáles incorporar"},
            {"id": "B", "texto": "Me afecta emocionalmente al principio pero luego las proceso"},
            {"id": "C", "texto": "Las agradezco y las implemento lo antes posible"},
            {"id": "D", "texto": "Pido más contexto para entender bien el feedback"},
        ],
        "skill_mapping": {
            "A": {"pensamiento_critico": 28, "autoevaluacion": 25, "toma_decisiones": 20},
            "B": {"inteligencia_emocional": 28, "resiliencia": 22, "manejo_estres": 20},
            "C": {"mentalidad_crecimiento": 30, "adaptabilidad": 22, "velocidad_aprendizaje": 20},
            "D": {"escucha_activa": 28, "pensamiento_analitico": 20, "comunicacion_verbal": 18},
        },
    },
    {
        "id": "q15",
        "question": "¿Cuál de estas frases te describe mejor?",
        "tipo": "opcion_multiple",
        "opciones": [
            {"id": "A", "texto": "Me gusta entender cómo funcionan las cosas por dentro"},
            {"id": "B", "texto": "Tengo muchas ideas y me encanta hacerlas realidad"},
            {"id": "C", "texto": "Soy bueno/a conectando con las personas y entendiendo sus necesidades"},
            {"id": "D", "texto": "Me enfoco en resultados — si algo no funciona, lo cambio rápido"},
        ],
        "skill_mapping": {
            "A": {"comprension_conceptual": 28, "pensamiento_sistemico": 25, "investigacion_academica": 20},
            "B": {"creatividad": 28, "innovacion": 25, "ideacion": 22},
            "C": {"empatia": 30, "investigacion_usuarios": 25, "servicio_cliente": 20},
            "D": {"orientacion_resultados": 30, "adaptabilidad": 22, "mejora_procesos": 25},
        },
    },
]


# ── Scoring ────────────────────────────────────────────────────────────────

def score_quiz(answers: dict[str, str]) -> dict[str, float]:
    """
    Convert quiz answers to skill scores.

    Args:
        answers: {"q1": "A", "q2": "C", ...}  — question id → option id

    Returns:
        {"pensamiento_analitico": 72.5, "creatividad": 65.0, ...}
        Scores are averaged across all questions that touched that skill.
        Capped at 100, floor at 0.
    """
    accumulated: dict[str, list[float]] = {}

    for question in ONBOARDING_QUIZ:
        qid = question["id"]
        answer = answers.get(qid)
        if answer is None:
            continue

        mapping = question["skill_mapping"].get(answer, {})
        for skill_slug, points in mapping.items():
            accumulated.setdefault(skill_slug, []).append(float(points))

    # Average all observations, clamp to [0, 100]
    final: dict[str, float] = {}
    for skill_slug, observations in accumulated.items():
        avg = sum(observations) / len(observations)
        final[skill_slug] = max(0.0, min(avg, 100.0))

    return final


def get_question(question_id: str) -> Optional[dict]:
    """Return a single question by id."""
    return next((q for q in ONBOARDING_QUIZ if q["id"] == question_id), None)


def get_all_questions() -> list[dict]:
    """Return all questions (for API serialization)."""
    return ONBOARDING_QUIZ


if __name__ == "__main__":
    # Test with a sample analytical profile
    sample_answers = {
        "q1": "C", "q2": "A", "q3": "A", "q4": "C",
        "q5": "A", "q6": "A", "q7": "C", "q8": "A",
        "q9": "A", "q10": "C", "q11": "A", "q12": "A",
        "q13": "A", "q14": "A", "q15": "A",
    }
    scores = score_quiz(sample_answers)
    print(f"✓ Quiz scored: {len(scores)} skills inferred")
    print("  Top 10 skills:")
    for skill, score in sorted(scores.items(), key=lambda x: -x[1])[:10]:
        print(f"    {skill}: {score:.1f}")

    # Test with a creative profile
    creative_answers = {
        "q1": "D", "q2": "B", "q3": "D", "q4": "A",
        "q5": "B", "q6": "B", "q7": "D", "q8": "D",
        "q9": "B", "q10": "A", "q11": "B", "q12": "C",
        "q13": "B", "q14": "C", "q15": "B",
    }
    scores2 = score_quiz(creative_answers)
    print(f"\n  Creative profile top 5:")
    for skill, score in sorted(scores2.items(), key=lambda x: -x[1])[:5]:
        print(f"    {skill}: {score:.1f}")
