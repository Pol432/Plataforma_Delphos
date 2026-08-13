
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
                            "xp_reward": 150
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
                            "xp_reward": 200
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
                            "xp_reward": 200
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
                            "xp_reward": 250
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
                            "xp_reward": 250
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
                            "xp_reward": 300
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
