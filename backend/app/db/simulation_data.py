
"""
Data structure for seeding simulations.
Hierarchy: Simulation -> Modules -> Tasks -> Resources/ModelAnswer
"""

SIMULATION_DATA = [
    {
        "simulation": {
            "company_name": "Skywork AI",
            "category_name": "Ingeniería y Tecnología",
            "title": "Ingeniería de Datos y Optimización de Flujos en Skywork AI",
            "slug": "skywork-ai-data-engineering-challenge",
            "short_description": "Asume el rol de un Ingeniero de Datos en Skywork AI y resuelve un desafío crítico de optimización de pipelines para nuestro sistema de sensores inteligentes.",
            "full_description": """En Skywork AI, estamos a la vanguardia de la inteligencia artificial aplicada a la logística y la automatización. Nuestra red global de sensores IoT recopila millones de puntos de datos por segundo para optimizar las cadenas de suministro en tiempo real. Sin embargo, un cuello de botella reciente en nuestro pipeline de ingesta de datos está amenazando la integridad de nuestro sistema. Tu misión, como nuestro nuevo Ingeniero de Datos, es diagnosticar, proponer y empezar a implementar una solución robusta y escalable. Esta simulación te sumergirá en los desafíos diarios de un ingeniero de datos de clase mundial, desde el análisis de código y la depuración de sistemas distribuidos hasta el diseño de arquitecturas de datos eficientes.""",
            "difficulty_level": "advanced",
            "estimated_hours": 6.5,
            "xp_reward": 1500,
            "lore_context": "Eres el ingeniero de datos senior contratado por Skywork AI para solucionar un cuello de botella crítico en un pipeline de ingestión de sensores en producción. Tendrás que equilibrar velocidad, costo y seguridad de los datos mientras trabajas contra el reloj.",
            "scaffolding_phase": "Guided",
            "real_world_constraints": ["presupuesto reducido", "ventana de despliegue nocturna", "dependencia de servicios legacy"],
            "immediate_feedback": {
                "on_failure_explanation": "Si tu solución introduce inconsistencias, revisa la sección 'Transactions & Batch Writes' en la documentación; evita escrituras sin commit y usa índices apropiados.",
                "links": ["https://docs.python.org/3/", "https://www.postgresql.org/docs/current/ddl-partitioning.html", "https://docs.sqlalchemy.org/"]
            },
            "skills_metrics_weights": {"Problem Solving": 0.5, "System Design": 0.3, "SQL": 0.2},
            "state": "published"
        },
        "modules": [
            {
                "module": {
                    "title": "Módulo 1: Diagnóstico del Pipeline de Ingesta",
                    "description": "Tu primer objetivo es analizar el pipeline actual, identificar el cuello de botella y proponer una solución técnica documentada.",
                    "order": 1,
                    "estimated_hours": 2.5
                },
                "tasks": [
                    {
                        "task": {
                            "title": "Tarea 1.1: Auditoría de la Ingesta de Datos en Tiempo Real",
                            "description": "Skywork AI está procesando más de 18 millones de eventos por hora desde una red global de sensores IoT. El pipeline actual falla bajo carga y está introduciendo inconsistencias de datos en la capa analítica. Se te entrega un módulo Python de ingestión que lee payloads JSON, normaliza campos y persiste registros en PostgreSQL. Tu misión es detectar fallas técnicas reales: procesamiento síncrono, falta de control de reintentos, manejo inadecuado de particiones temporales, uso de `pandas` en loops innecesarios y ausencia de transacciones de escritura por lote. Debes entregar un informe técnico con una propuesta concreta de refactorización que incluya: (1) arquitectura de procesamiento con `ThreadPoolExecutor` o `asyncio`, (2) estrategia de reintentos y backoff exponencial, (3) modelado de esquema para eventos de sensor con claves de partición y (4) recomendación de `SQLAlchemy` + `psycopg2` o `asyncpg` para escrituras masivas. Además, debes especificar cómo validarías la integridad de los datos y la latencia p95 del pipeline.",
                            "order": 1,
                            "task_type": "submission",
                            "instructor_name": "Dra. Aris Thorne",
                            "instructor_role": "Principal Data Architect, Skywork AI",
                            "estimated_minutes": 75,
                            "xp_reward": 150,
                            "lore_context": "Revisa los logs, los scripts de ingestión y plantea hipótesis; documenta el pipeline propuesto en 600-800 palabras.",
                            "scaffolding_phase": "Guided",
                            "real_world_constraints": ["picos de carga impredecibles", "dependencia de proveedores externos"],
                            "immediate_feedback": {"on_failure_explanation": "Chequea los patrones anti-patrón de uso de pandas en streaming; prioriza operaciones vectorizadas.", "links": ["https://pandas.pydata.org/docs/", "https://docs.python.org/3/library/concurrent.futures.html"]},
                            "skills_metrics_weights": {"Problem Solving": 0.6, "Python": 0.25, "Data Engineering": 0.15}
                        },
                        "resources": [
                            {"name": "Código Fuente: ingest_sensor_data.py", "resource_type": "file", "url": "/resources/simulations/skywork/ingest_sensor_data.py"},
                            {"name": "Documentación del Schema de Sensores", "resource_type": "document", "url": "/resources/simulations/skywork/sensor_schema.pdf"},
                            {"name": "Métricas de Performance del Pipeline (Gráficos)", "resource_type": "dashboard", "url": "/resources/simulations/skywork/pipeline_performance.png"}
                        ],
                        "model_answer": {
                            "description": "La respuesta de alto nivel debía identificar que el cuello de botella principal era el procesamiento en serie, con escrituras individuales a la base de datos y falta de gestión de errores por lote. La solución óptima incluía refactorizar el flujo a un modelo productor-consumidor con workers, usar `ThreadPoolExecutor` o `asyncio` para paralelizar la normalización, introducir reintentos con backoff exponencial y consolidar las inserciones con `bulk_insert` o `insertmanyvalues` mediante SQLAlchemy. También se debía recomendar separar la ingesta y el enriquecimiento, aplicar particiones por día y usar checksums de integridad para validar mensajes duplicados o corruptos antes de persistirlos.",
                            "key_learnings": [
                                "Auditoría de pipelines de datos en producción.",
                                "Diseño de ingestión escalable en Python.",
                                "Optimización de carga con SQLAlchemy y PostgreSQL.",
                                "Control de tolerancia a fallos y observabilidad de latencia."
                            ]
                        }
                    },
                    {
                        "task": {
                            "title": "Tarea 1.2: Re-diseño de la Consulta SQL de Agregación",
                            "description": "El dashboard de análisis de datos está experimentando timeouts severos durante los reportes ejecutivos. La causa principal es una consulta de agregación en PostgreSQL que resume los eventos térmicos y de movimiento de una flota de sensores IoT. Se te ha proporcionado la consulta actual, que genera múltiples escaneos de tabla y hace joins costosos contra tablas de eventos históricos. Tu tarea es re-escribirla para optimizar el rendimiento aplicando CTEs, window functions, filtrado temprano y diseño de índices. Debes justificar por qué tu propuesta reduce el costo de ejecución, qué columnas deberían indexarse y cómo manejarías la partición del dataset para mantener reportes por hora, día y semana sin degradar el rendimiento. Tu respuesta debe incluir una propuesta de SQL y una explicación técnica breve sobre el plan de ejecución esperado.",
                            "order": 2,
                            "task_type": "submission",
                            "instructor_name": "Dra. Aris Thorne",
                            "instructor_role": "Principal Data Architect, Skywork AI",
                            "estimated_minutes": 75,
                            "xp_reward": 200,
                            "lore_context": "Optimiza la consulta para permitir dashboards en tiempo real; explica los trade-offs de índice vs partición.",
                            "scaffolding_phase": "Intermediate",
                            "real_world_constraints": ["ventana de mantenimiento corta", "limites de I/O"],
                            "immediate_feedback": {"on_failure_explanation": "Si la consulta sigue siendo lenta, instrumenta con EXPLAIN ANALYZE y busca scans secuenciales; considera materialized views.", "links": ["https://www.postgresql.org/docs/current/using-explain.html"]},
                            "skills_metrics_weights": {"SQL": 0.7, "Performance Tuning": 0.3}
                        },
                        "resources": [
                            {"name": "Consulta SQL Lenta: get_sensor_summary.sql", "resource_type": "file", "url": "/resources/simulations/skywork/get_sensor_summary.sql"},
                            {"name": "Plan de Ejecución de la Consulta (Actual)", "resource_type": "image", "url": "/resources/simulations/skywork/query_plan.png"}
                        ],
                        "model_answer": {
                            "description": "Una consulta optimizada debía pre-filtrar primero por rango de tiempo, aplicar CTEs para reducir cardinalidad antes de hacer agregaciones y utilizar `SUM() OVER (PARTITION BY ...)` o agregados condicionales cuando la lógica lo permitía. El plan esperado debía evitar subconsultas correlacionadas y reescribir joins costosos como joins a tablas históricas sin filtros. Además, se debía recomendar un índice compuesto en `sensor_id`, `event_time` y `event_type`, con particiones por día o por mes según el volumen de eventos para mantener el reporte ejecutable en tiempo real.",
                            "key_learnings": [
                                "Optimización de consultas SQL avanzadas.",
                                "Uso de CTEs y Window Functions.",
                                "Análisis de planes de ejecución de consulta.",
                                "Diseño de índices y particionamiento para analytics."
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "simulation": {
            "company_name": "Apex Leadership Group",
            "category_name": "Negocios y Finanzas",
            "title": "Liderazgo Estratégico y Sostenibilidad en Apex Leadership Group",
            "slug": "apex-leadership-sustainability-strategy",
            "short_description": "Como Asesor Estratégico del CEO en Apex Leadership Group, debes navegar una crisis reputacional y desarrollar un nuevo marco de KPIs para el bienestar y la sostenibilidad.",
            "full_description": """Apex Leadership Group, una consultora líder en desarrollo de liderazgo, se enfrenta a un desafío interno y externo. Un informe reciente ha revelado una desconexión entre nuestra imagen pública de 'liderazgo consciente' y las métricas de bienestar interno. El CEO te ha encargado liderar una fuerza de tarea para abordar esta crisis de frente. Tu responsabilidad es doble: primero, analizar los datos directivos para entender la raíz del problema; segundo, proponer un nuevo cuadro de mando integral (Balanced Scorecard) que alinee el rendimiento financiero con la sostenibilidad corporativa y el bienestar de los empleados. Esta simulación pondrá a prueba tu perspicacia para los negocios, tu inteligencia emocional y tu capacidad para tomar decisiones basadas en datos en un entorno de alta presión.""",
            "difficulty_level": "intermediate",
            "estimated_hours": 5.0,
            "xp_reward": 1200,
            "lore_context": "Eres un asesor estratégico encargado por el CEO para recuperar la reputación de Apex y redefinir KPIs que equilibren rendimiento financiero y bienestar humano.",
            "scaffolding_phase": "Guided",
            "real_world_constraints": ["recortes presupuestarios", "resistencia al cambio interno"],
            "immediate_feedback": {"on_failure_explanation": "Si tu cuadro de mando no recibe aceptación, vincula KPIs a objetivos financieros y presenta ROI estimado; revisa plantillas GRI.", "links": ["https://www.globalreporting.org/", "https://hbr.org/"]},
            "skills_metrics_weights": {"Strategic Thinking": 0.5, "Data Analysis": 0.3, "Communication": 0.2},
            "state": "published"
        },
        "modules": [
            {
                "module": {
                    "title": "Módulo 1: Análisis de Situación y Definición de KPIs",
                    "description": "Sumérgete en los datos de la empresa, desde financieros hasta encuestas de clima laboral, para construir un diagnóstico preciso.",
                    "order": 1,
                    "estimated_hours": 3.0
                },
                "tasks": [
                    {
                        "task": {
                            "title": "Tarea 1.1: Interpretación del Dashboard Directivo y Diagnóstico del Problema",
                            "description": "Se te ha dado acceso al dashboard de Power BI de la dirección. Analiza las métricas de rotación de personal, las encuestas de compromiso (eNPS), y los resultados financieros trimestrales. Cruza los datos y redacta un memorando ejecutivo para el CEO resumiendo tus hallaz-azgos clave y diagnosticando las causas probables de la crisis de bienestar.",
                            "order": 1,
                            "task_type": "submission",
                            "instructor_name": "John Maxwell",
                            "instructor_role": "Fundador y CEO, Apex Leadership Group",
                            "estimated_minutes": 90,
                            "xp_reward": 200,
                            "lore_context": "Interpreta el dashboard ejecutivo y prepara un memorando ejecutivo claro y accionable destinado al CEO y al board.",
                            "scaffolding_phase": "Guided",
                            "real_world_constraints": ["política interna", "plazos trimestrales"],
                            "immediate_feedback": {"on_failure_explanation": "Si tu diagnóstico carece de evidencia, incluye visualizaciones y referencias a métricas concretas; revisa ejemplos de memorandos ejecutivos.", "links": ["https://hbr.org/", "https://www.mckinsey.com/"]},
                            "skills_metrics_weights": {"Communication": 0.6, "Data Analysis": 0.4}
                        },
                        "resources": [
                            {"name": "Acceso al Dashboard Directivo (Interactivo)", "resource_type": "dashboard", "url": "/resources/simulations/apex/executive_dashboard.pbix"},
                            {"name": "Informe de Prensa sobre la Crisis", "resource_type": "document", "url": "/resources/simulations/apex/press_report.pdf"}
                        ],
                        "model_answer": {
                            "description": "El análisis correcto debería correlacionar un aumento en la rotación de personal de alto rendimiento con una disminución en el puntaje de 'Balance Vida-Trabajo' en las encuestas, a pesar de que los ingresos trimestrales aumentaron. El memo debería concluir que la cultura de 'crecimiento a toda costa' está generando agotamiento y es insostenible.",
                            "key_learnings": [
                                "Análisis de datos de negocio multi-dimensional.",
                                "Interpretación de KPIs de RRHH y Financieros.",
                                "Comunicación ejecutiva concisa (Estilo Memorando)."
                            ]
                        }
                    },
                    {
                        "task": {
                            "title": "Tarea 1.2: Diseño de un Nuevo Cuadro de Mando de Sostenibilidad (ESG & Bienestar)",
                            "description": "Basado en tu diagnóstico, diseña un nuevo conjunto de KPIs (Indicadores Clave de Rendimiento) que la empresa debería adoptar. Estos deben cubrir las áreas de Sostenibilidad Ambiental, Social y de Gobernanza (ESG), así como métricas específicas de bienestar del empleado. Presenta tus KPIs en una estructura de Cuadro de Mando Integral, justificando cada uno.",
                            "order": 2,
                            "task_type": "submission",
                            "instructor_name": "John Maxwell",
                            "instructor_role": "Fundador y CEO, Apex Leadership Group",
                            "estimated_minutes": 90,
                            "xp_reward": 250,
                            "lore_context": "Diseña KPIs prácticos y defendibles para medidas de sostenibilidad que el board pueda implementar en 12 meses.",
                            "scaffolding_phase": "Intermediate",
                            "real_world_constraints": ["datos incompletos", "métricas no estandarizadas"],
                            "immediate_feedback": {"on_failure_explanation": "Si tus KPIs son difíciles de medir, agrega métricas proxy y una ruta de instrumentación; revisa estándares GRI.", "links": ["https://www.globalreporting.org/standards/"]},
                            "skills_metrics_weights": {"Strategic Thinking": 0.5, "ESG": 0.3, "Measurement": 0.2}
                        },
                        "resources": [
                            {"name": "Guía sobre Cuadros de Mando Integral (Kaplan & Norton)", "resource_type": "document", "url": "/resources/simulations/apex/balanced_scorecard_guide.pdf"},
                            {"name": "Ejemplos de Informes de Sostenibilidad (Reportes GRI)", "resource_type": "link", "url": "https://www.globalreporting.org/"}
                        ],
                        "model_answer": {
                            "description": "Una propuesta sólida incluiría KPIs como: 'Reducción de la Huella de Carbono (tCO2e)', '% de Mujeres en Posiciones de Liderazgo', 'Índice de Bienestar Psicológico (basado en encuestas validadas)', y 'Horas de Formación por Empleado'. Cada KPI debe estar justificado en cómo impacta la estrategia a largo plazo y la mitigación de la crisis actual.",
                            "key_learnings": [
                                "Diseño de KPIs y métricas de negocio.",
                                "Principios de Sostenibilidad Corporativa (ESG).",
                                "Aplicación del modelo de Cuadro de Mando Integral."
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "simulation": {
            "company_name": "Hospital Central San Lucas",
            "category_name": "Ciencias de la Salud",
            "title": "Diagnóstico Clínico de Urgencias en el Hospital Central San Lucas",
            "slug": "san-lucas-hospital-emergency-diagnostics",
            "short_description": "Eres un médico residente en la sala de urgencias del Hospital San Lucas. Un paciente llega con síntomas complejos y tu deber es realizar el triaje, diagnóstico diferencial y proponer un plan de acción inmediato.",
            "full_description": """El tiempo es el factor más crítico en la medicina de urgencias. En el Hospital Central San Lucas, nuestro equipo se enfrenta a decisiones de vida o muerte cada minuto. Esta simulación te coloca en el centro de la acción. Un paciente de 45 años ingresa a urgencias con un cuadro de dolor torácico agudo, disnea y mareos. No hay un diagnóstico obvio. ¿Es un evento cardíaco? ¿Una embolia pulmonar? ¿Un ataque de ansiedad agudo? Utilizando los protocolos del hospital, tu conocimiento médico y tu capacidad de razonamiento bajo presión, deberás analizar la historia clínica, interpretar los resultados de las pruebas iniciales y formular un diagnóstico diferencial coherente para salvar la vida del paciente.""",
            "difficulty_level": "advanced",
            "estimated_hours": 4.0,
            "xp_reward": 1600,
            "lore_context": "Eres el residente de urgencias encargado del primer triage; toma decisiones basadas en probabilidad, priorizando intervenciones con mayor impacto en supervivencia.",
            "scaffolding_phase": "Guided",
            "real_world_constraints": ["recursos limitados", "presión de tiempo"],
            "immediate_feedback": {"on_failure_explanation": "Si pasas por alto un diagnóstico crítico, revisa el algoritmo ABCDE y protocolos locales; consulta guías de la AHA.", "links": ["https://www.ahajournals.org/", "https://www.who.int/"]},
            "skills_metrics_weights": {"Clinical Reasoning": 0.6, "Decision Making": 0.3, "Communication": 0.1},
            "state": "published"
        },
        "modules": [
            {
                "module": {
                    "title": "Módulo 1: Triaje y Diagnóstico Diferencial",
                    "description": "Desde la llegada del paciente hasta la formulación de las hipótesis diagnósticas principales.",
                    "order": 1,
                    "estimated_hours": 2.0
                },
                "tasks": [
                    {
                        "task": {
                            "title": "Tarea 1.1: Análisis de Historia Clínica y Signos Vitales",
                            "description": "Revisa la historia clínica del paciente, sus antecedentes, y los signos vitales tomados al ingreso por enfermería. Basado en esta información inicial, enumera al menos tres posibles diagnósticos diferenciales (del más al menos probable), justificando cada uno basándote en la evidencia presentada. Tu respuesta debe seguir el formato de una nota clínica estructurada (SOAP).",
                            "order": 1,
                            "task_type": "submission",
                            "instructor_name": "Dra. Elena Rivas",
                            "instructor_role": "Jefa de Medicina de Urgencias, H.C. San Lucas",
                            "estimated_minutes": 60,
                            "xp_reward": 250,
                            "lore_context": "Estructura una nota clínica SOAP concisa que priorice hallazgos y decisiones inmediatas; considera recursos de sala de urgencias.",
                            "scaffolding_phase": "Guided",
                            "real_world_constraints": ["camilla ocupada", "personal limitado"],
                            "immediate_feedback": {"on_failure_explanation": "Si tu SOAP carece de prioridades, enfócate en 'must-do' actions y medidas inmediatas; revisa guías locales.", "links": ["https://www.ncbi.nlm.nih.gov/pmc/"]},
                            "skills_metrics_weights": {"Clinical Reasoning": 0.7, "Documentation": 0.3}
                        },
                        "resources": [
                            {"name": "Historia Clínica del Paciente: Juan Pérez", "resource_type": "document", "url": "/resources/simulations/sanlucas/historia_clinica_jp.pdf"},
                            {"name": "Hoja de Signos Vitales de Triaje", "resource_type": "image", "url": "/resources/simulations/sanlucas/signos_vitales_jp.jpg"}
                        ],
                        "model_answer": {
                            "description": "La respuesta correcta debe identificar el Infarto Agudo de Miocardio (IAM), la Embolia Pulmonar (EP) y la Disección Aórtica como los tres diagnósticos diferenciales más críticos. La justificación para el IAM se basaría en el dolor torácico y los factores de riesgo (si los hay en la historia). La EP se justificaría por la disnea súbita. La Disección Aórtica por la severidad del dolor. La nota SOAP debe estar bien estructurada.",
                            "key_learnings": [
                                "Metodología de diagnóstico diferencial.",
                                "Interpretación de signos vitales e historias clínicas.",
                                "Redacción de notas clínicas (Formato SOAP)."
                            ]
                        }
                    },
                    {
                        "task": {
                            "title": "Tarea 1.2: Solicitud e Interpretación de Pruebas de Diagnóstico",
                            "description": "Ahora debes actuar. Basado en tu diagnóstico diferencial, elabora una solicitud de pruebas de laboratorio y de imagen. Debes solicitar SOLAMENTE las pruebas esenciales para confirmar o descartar tus hipótesis principales, justificando por qué cada prueba es necesaria en este momento crítico (ej. 'Pido un EKG para buscar elevación del segmento ST, sugestivo de IAM').",
                            "order": 2,
                            "task_type": "submission",
                            "instructor_name": "Dra. Elena Rivas",
                            "instructor_role": "Jefa de Medicina de Urgencias, H.C. San Lucas",
                            "estimated_minutes": 60,
                            "xp_reward": 300,
                            "lore_context": "Solicita solo pruebas esenciales justificadas por probabilidad pre-test; prioriza tests con mayor valor diagnóstico inmediato.",
                            "scaffolding_phase": "Final Challenge",
                            "real_world_constraints": ["tiempo crítico", "disponibilidad limitada de imagen"],
                            "immediate_feedback": {"on_failure_explanation": "Si solicitas pruebas innecesarias, justificar el riesgo y costo; revisa guías de urgencias.", "links": ["https://www.ncbi.nlm.nih.gov/pmc/"]},
                            "skills_metrics_weights": {"Decision Making": 0.6, "Clinical Knowledge": 0.4}
                        },
                        "resources": [
                            {"name": "Formulario de Solicitud de Pruebas del Hospital", "resource_type": "form", "url": "/resources/simulations/sanlucas/lab_request_form.html"}
                        ],
                        "model_answer": {
                            "description": "Las solicitudes esenciales serían: 1) Electrocardiograma (EKG) de 12 derivaciones (para IAM). 2) Troponinas Cardíacas (marcador de daño miocárdico). 3) Dímero-D (para ayudar a descartar EP si el riesgo es bajo/intermedio). 4) Angio-TAC de tórax (Gold Standard para EP y también puede mostrar disección aórtica). Solicitar un panel metabólico completo o un hemograma completo también es estándar y aceptable.",
                            "key_learnings": [
                                "Toma de decisiones clínicas bajo presión.",
                                "Uso racional de pruebas diagnósticas.",
                                "Correlación entre pruebas y patologías específicas."
                            ]
                        }
                    }
                ]
            }
        ]
    }
]

# Vocational simulations focused on Generation Z career guidance
NEW_VOCATIONAL_SIMULATIONS = [
    {"simulation": {
        "title": "Marketing Digital: Campaña de Lanzamiento Viral",
        "slug": "marketing-digital-campana-lanzamiento-viral",
        "short_description": "Diseña y ejecuta una estrategia de lanzamiento digital para una marca emergente enfocada en audiencias Z.",
        "company_id": 4,
        "category_id": 4,
        "lore_context": "Eres el estratega digital contratado por una start-up de moda sostenible que busca volverse viral sin presupuesto de medios. Debes crear una campaña orgánica que genere impacto y métricas reales en 30 días.",
        "scaffolding_phase": "Guided",
        "real_world_constraints": ["presupuesto recortado", "algoritmo de plataforma cambiante"],
        "immediate_feedback": {"links": ["https://learndigital.withgoogle.com/","https://support.facebook.com/business/"], "on_failure_explanation": "Si la campaña no genera tracción, revisa los A/B tests del mensaje y el CTA; prioriza contenido generado por usuarios y microinfluencers con métricas de engagement claras."},
        "skills_metrics_weights": {"Content Strategy": 0.4, "Analytics": 0.3, "Community Engagement": 0.3}
    }},
    {"simulation": {
        "title": "Derecho: Defensa en Simulación de Audiencia Pública",
        "slug": "derecho-defensa-simulacion-audiencia",
        "short_description": "Prepara la defensa legal para un caso de uso público complejo con énfasis en argumento y ética profesional.",
        "company_id": 5,
        "category_id": 5,
        "lore_context": "Asumes el rol de abogado defensor en una audiencia pública donde debes equilibrar derecho, ética y opinión pública para proteger los derechos de tu cliente.",
        "scaffolding_phase": "Intermediate",
        "real_world_constraints": ["presión mediática", "tiempo limitado para pruebas"],
        "immediate_feedback": {"links": ["https://www.icj-cij.org/","https://www.brookings.edu/"], "on_failure_explanation": "Si tus argumentos fallan en la audiencia, documenta las lagunas probatorias y propone medidas remediales; revisa doctrina y precedentes relevantes."},
        "skills_metrics_weights": {"Argumentation": 0.45, "Legal Research": 0.35, "Ethical Reasoning": 0.2}
    }},
    {"simulation": {
        "title": "Psicología: Intervención en Crisis Juvenil",
        "slug": "psicologia-intervencion-crisis-juvenil",
        "short_description": "Atiende una sesión de intervención para un joven con riesgo de aislamiento social y de rendimiento académico decreciente.",
        "company_id": 6,
        "category_id": 6,
        "lore_context": "Eres psicólogo clínico en un centro universitario; debes evaluar, intervenir y diseñar un plan breve de seguimiento para un estudiante en crisis.",
        "scaffolding_phase": "Guided",
        "real_world_constraints": ["recursos limitados del centro", "resistencia del paciente"],
        "immediate_feedback": {"links": ["https://www.apa.org/","https://www.who.int/mental_health"], "on_failure_explanation": "Si la intervención no reduce riesgo percibido, considera derivación a servicios especializados y revisa estrategias de motivación y alianza terapéutica."},
        "skills_metrics_weights": {"Clinical Assessment": 0.4, "Communication": 0.35, "Crisis Management": 0.25}
    }},
    {"simulation": {
        "title": "Arquitectura: Propuesta de Rehabilitación Urbana",
        "slug": "arquitectura-propuesta-rehabilitacion-urbana",
        "short_description": "Diseña una intervención arquitectónica para revitalizar una plaza pública con enfoque sostenible y comunitario.",
        "company_id": 7,
        "category_id": 7,
        "lore_context": "Eres el arquitecto a cargo de rehabilitar una plaza deteriorada; debes integrar diseño, viabilidad y participación ciudadana en una propuesta ejecutable.",
        "scaffolding_phase": "Intermediate",
        "real_world_constraints": ["normativas municipales", "presupuesto comunitario"],
        "immediate_feedback": {"links": ["https://www.archdaily.com/","https://www.un.org/sustainabledevelopment/"], "on_failure_explanation": "Si la propuesta no obtiene aceptación, ajusta el diseño para cumplir regulaciones locales y prioriza intervenciones de alto impacto social con bajo costo."},
        "skills_metrics_weights": {"Design": 0.45, "Regulation Knowledge": 0.25, "Community Engagement": 0.3}
    }},
    {"simulation": {
        "title": "Administración: Plan de Recuperación Operativa",
        "slug": "administracion-plan-recuperacion-operativa",
        "short_description": "Elabora un plan operativo para recuperar la eficiencia tras una caída de productividad en una PYME familiar.",
        "company_id": 8,
        "category_id": 8,
        "lore_context": "Eres gerente de operaciones llamado para recuperar la productividad de una PYME con problemas de procesos y moral del equipo.",
        "scaffolding_phase": "Guided",
        "real_world_constraints": ["conflictos familiares internos", "recursos humanos limitados"],
        "immediate_feedback": {"links": ["https://www.mckinsey.com/","https://hbr.org/"], "on_failure_explanation": "Si las medidas no mejoran productividad, documenta cuellos de botella y propone cambios incrementales priorizados por ROI; incluye plan de comunicación."},
        "skills_metrics_weights": {"Process Improvement": 0.4, "Change Management": 0.35, "Stakeholder Communication": 0.25}
    }},
    {"simulation": {
        "title": "Finanzas: Modelado Financiero para Startups",
        "slug": "finanzas-modelado-financiero-startups",
        "short_description": "Construye un modelo financiero que permita tomar decisiones de inversión y estimar runway para una startup tecnológica.",
        "company_id": 9,
        "category_id": 9,
        "lore_context": "Eres analista financiero en una VC y debes modelar escenarios de ingresos, costos y runway para evaluar una ronda seed.",
        "scaffolding_phase": "Intermediate",
        "real_world_constraints": ["incertidumbre de mercado", "datos históricos limitados"],
        "immediate_feedback": {"links": ["https://www.investopedia.com/","https://www.cfainstitute.org/"], "on_failure_explanation": "Si el modelo falla, revisa supuestos de crecimiento y sensibilidad; crea escenarios pesimista/realista/optimista y documenta hipótesis."},
        "skills_metrics_weights": {"Financial Modeling": 0.5, "Scenario Analysis": 0.3, "Presentation": 0.2}
    }},
    {"simulation": {
        "title": "Diseño Gráfico: Identidad Visual para Marca Emerging",
        "slug": "diseno-grafico-identidad-visual",
        "short_description": "Desarrolla una identidad visual y manual de marca para una microempresa de productos artesanales.",
        "company_id": 10,
        "category_id": 10,
        "lore_context": "Eres diseñador(a) gráfico contratado para crear la identidad visual de una marca que combina tradición y modernidad.",
        "scaffolding_phase": "Guided",
        "real_world_constraints": ["plazos ajustados", "presupuesto de producción"],
        "immediate_feedback": {"links": ["https://www.behance.net/","https://www.adobe.com/creativecloud.html"], "on_failure_explanation": "Si la identidad no comunica el posicionamiento, revisa target audience y realiza prototipos de packaging con usuarios; ajusta paleta y tipografía."},
        "skills_metrics_weights": {"Visual Design": 0.5, "Brand Strategy": 0.3, "UX": 0.2}
    }},
    {"simulation": {
        "title": "Ingeniería Industrial: Optimización de Línea de Producción",
        "slug": "ingenieria-industrial-optimizacion-linea-produccion",
        "short_description": "Rediseña una línea de producción para reducir tiempos muertos y aumentar rendimiento con mínima inversión.",
        "company_id": 11,
        "category_id": 11,
        "lore_context": "Eres ingeniero industrial contratado para optimizar una planta con equipos obsoletos y alta variabilidad en eficiencia.",
        "scaffolding_phase": "Intermediate",
        "real_world_constraints": ["paradas no planificadas", "limitaciones de stock"],
        "immediate_feedback": {"links": ["https://asq.org/","https://lean.org/"], "on_failure_explanation": "Si las mejoras no reducen tiempos muertos, realiza un mapeo de flujo de valor más detallado y prioriza cambios con mayor impacto por bajo costo."},
        "skills_metrics_weights": {"Process Optimization": 0.45, "Lean Tools": 0.3, "Data Analysis": 0.25}
    }},
    {"simulation": {
        "title": "Ciencias de la Computación: Arquitectura de Microservicios",
        "slug": "cs-arquitectura-microservicios",
        "short_description": "Diseña la arquitectura de microservicios para una aplicación de alto tráfico con necesidades de escalado y resiliencia.",
        "company_id": 12,
        "category_id": 12,
        "lore_context": "Eres arquitecto backend encargado de migrar un monolito crítico a microservicios manteniendo SLAs y minimizando downtime.",
        "scaffolding_phase": "Guided",
        "real_world_constraints": ["compatibilidad retroactiva", "limites de infraestructura"],
        "immediate_feedback": {"links": ["https://microservices.io/","https://docs.kubernetes.io/"], "on_failure_explanation": "Si la migración introduce regresiones, instrumenta trazas distribuidas y reduce el blast radius; implementa pruebas contractuales entre servicios."},
        "skills_metrics_weights": {"System Design": 0.5, "Reliability Engineering": 0.3, "API Design": 0.2}
    }},
    {"simulation": {
        "title": "Ingeniería Civil: Evaluación de Riesgo Estructural",
        "slug": "ingenieria-civil-evaluacion-riesgo-estructural",
        "short_description": "Evalúa la seguridad de un puente urbano y propone intervenciones preventivas priorizadas.",
        "company_id": 13,
        "category_id": 13,
        "lore_context": "Eres ingeniero civil en una inspección urgente tras reportes de fisuras; debes valorar riesgo y presentar un plan de mitigación.",
        "scaffolding_phase": "Final Challenge",
        "real_world_constraints": ["tránsito crítico", "presupuesto municipal limitado"],
        "immediate_feedback": {"links": ["https://www.asce.org/","https://www.fhwa.dot.gov/"], "on_failure_explanation": "Si tu evaluación subestima riesgo, incorpora inspecciones instrumentadas y modelado estructural más detallado; prioriza seguridad pública."},
        "skills_metrics_weights": {"Risk Assessment": 0.5, "Structural Analysis": 0.3, "Project Planning": 0.2}
    }},
    {"simulation": {
        "title": "Medicina: Triage y Manejo en Unidad de Urgencias",
        "slug": "medicina-triage-manejo-urgencias",
        "short_description": "Realiza triage y maneja un caso crítico en urgencias optimizando tiempos y recursos en un hospital regional.",
        "company_id": 14,
        "category_id": 14,
        "lore_context": "Eres médico de urgencias en turno nocturno; llega un paciente con signos vitales inestables y debes priorizar acciones que salven vida.",
        "scaffolding_phase": "Final Challenge",
        "real_world_constraints": ["recursos limitados", "alta ocupación de camas"],
        "immediate_feedback": {"links": ["https://www.who.int/","https://www.nejm.org/"], "on_failure_explanation": "Si tu manejo inicial no estabiliza al paciente, revisa algoritmos ABC, ordena pruebas prioritarias y considera transferencias; documenta decisiones."},
        "skills_metrics_weights": {"Clinical Decision Making": 0.5, "Acute Management": 0.3, "Documentation": 0.2}
    }},
    {"simulation": {
        "title": "Biología: Diseño Experimental en Laboratorio",
        "slug": "biologia-diseno-experimental-laboratorio",
        "short_description": "Diseña un experimento controlado para evaluar efecto de un tratamiento sobre cultivo celular.",
        "company_id": 15,
        "category_id": 15,
        "lore_context": "Eres investigador junior liderando un experimento donde debes definir controles, replicación y análisis estadístico con recursos de laboratorio limitados.",
        "scaffolding_phase": "Intermediate",
        "real_world_constraints": ["reactivos limitados", "variabilidad biológica"],
        "immediate_feedback": {"links": ["https://www.ncbi.nlm.nih.gov/","https://www.protocols.io/"], "on_failure_explanation": "Si el experimento falla, revisa diseño estadístico, aumente replicación y verifica calidad de reactivos; documenta pasos reproducibles."},
        "skills_metrics_weights": {"Experimental Design": 0.45, "Data Analysis": 0.35, "Lab Techniques": 0.2}
    }},
    {"simulation": {
        "title": "Comunicación Social: Gestión de Crisis en Medios",
        "slug": "comunicacion-gestion-crisis-medios",
        "short_description": "Maneja la comunicación y reputación de una organización durante una crisis mediática emergente.",
        "company_id": 16,
        "category_id": 16,
        "lore_context": "Eres el responsable de comunicaciones durante una crisis pública; debes definir mensajes, canales y plan de respuesta para mitigar impacto reputacional.",
        "scaffolding_phase": "Guided",
        "real_world_constraints": ["difusión viral", "opinión pública polarizada"],
        "immediate_feedback": {"links": ["https://www.cision.com/","https://www.prsa.org/"], "on_failure_explanation": "Si la respuesta empeora la crisis, evalúa tono y timming; prioriza transparencia y acciones concretas; ajusta mensaje según audiencia."},
        "skills_metrics_weights": {"Message Strategy": 0.4, "Channel Management": 0.3, "Crisis Analysis": 0.3}
    }},
    {"simulation": {
        "title": "Relaciones Internacionales: Negociación Multilateral",
        "slug": "relaciones-internacionales-negociacion-multilateral",
        "short_description": "Participa en una negociación multilateral para alcanzar un acuerdo regional sobre comercio sostenible.",
        "company_id": 17,
        "category_id": 17,
        "lore_context": "Eres delegado en una cumbre regional; debes negociar cláusulas que equilibren desarrollo económico y sostenibilidad entre países con intereses contrapuestos.",
        "scaffolding_phase": "Intermediate",
        "real_world_constraints": ["presión diplomática", "plazos de cumbre"],
        "immediate_feedback": {"links": ["https://www.un.org/","https://www.wto.org/"], "on_failure_explanation": "Si la negociación fracasa, documenta puntos de fricción y propone concesiones climáticas o económicas equivalentes; prioriza gobernanza y seguimiento."},
        "skills_metrics_weights": {"Negotiation": 0.45, "Policy Analysis": 0.35, "Diplomacy": 0.2}
    }},
    {"simulation": {
        "title": "Ingeniería Ambiental: Plan de Remediación Local",
        "slug": "ingenieria-ambiental-plan-remediacion-local",
        "short_description": "Diseña un plan de remediación para un área contaminada y establece indicadores de éxito a 12 meses.",
        "company_id": 18,
        "category_id": 18,
        "lore_context": "Eres ingeniero ambiental liderando un proyecto comunitario para remediar un sitio industrial contaminado con recursos públicos limitados.",
        "scaffolding_phase": "Final Challenge",
        "real_world_constraints": ["comunidad escéptica", "limitaciones presupuestarias"],
        "immediate_feedback": {"links": ["https://www.epa.gov/","https://www.unep.org/"], "on_failure_explanation": "Si el plan no remedia contaminantes, prioriza medidas de contención y monitoreo; revisa tecnologías de biorremediación y su costo-beneficio."},
        "skills_metrics_weights": {"Environmental Assessment": 0.45, "Project Management": 0.3, "Community Outreach": 0.25}
    }}
]


# --- PARCHE PARA UNIR LAS NUEVAS SIMULACIONES ---
for item in NEW_VOCATIONAL_SIMULATIONS:
    # 1. Agregar la lista de módulos que faltaba
    if 'modules' not in item:
        item['modules'] = []
    
    # 2. Agregar los campos de texto que exige el script de la base de datos
    sim_data = item['simulation']
    if 'company_name' not in sim_data:
        # Genera un nombre de empresa ficticio basado en el título (ej. "Derecho Corp")
        sim_data['company_name'] = sim_data['title'].split(':')[0] + " Corp"
        
    if 'category_name' not in sim_data:
        sim_data['category_name'] = "Simulación Vocacional"

# Evitamos duplicar la lista si ejecutas el archivo varias veces
if len(SIMULATION_DATA) == 3:
    SIMULATION_DATA.extend(NEW_VOCATIONAL_SIMULATIONS)
