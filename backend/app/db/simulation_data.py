
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
                            "title": "Tarea 1.1: Análisis de Código del Script de Ingesta",
                            "description": "Se te ha entregado el script `ingest_sensor_data.py`, que actualmente está fallando bajo carga. Analiza el código, identifica las ineficiencias (ej. procesamiento síncrono, falta de manejo de errores, consultas N+1) y redacta un informe técnico con tus hallazgos y recomendaciones de refactorización.",
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
                            "description": "La solución óptima implicaba identificar el bucle de procesamiento s-incrono como el principal cuello de botella. Las recomendaciones clave debían incluir la paralelización con `ThreadPoolExecutor`, la implementación de un sistema de colas (como RabbitMQ o Kafka) para desacoplar la ingesta y el procesamiento, y el uso de `bulk_insert` en la base de datos para evitar escrituras individuales.",
                            "key_learnings": [
                                "Identificación de cuellos de botella en código Python.",
                                "Principios de procesamiento asíncrono y en lotes.",
                                "Redacción de informes técnicos de ingeniería."
                            ]
                        }
                    },
                    {
                        "task": {
                            "title": "Tarea 1.2: Re-diseño de la Consulta SQL de Agregación",
                            "description": "El dashboard de análisis de datos está experimentando timeouts. La causa principal es una consulta de agregación ineficiente en la base de datos SQL Server que resume los datos de los sensores. Se te ha proporcionado la consulta actual. Tu tarea es re-escribirla para optimizar su rendimiento, utilizando técnicas avanzadas como CTEs (Common Table Expressions), Window Functions y una correcta indexación.",
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
                            "description": "Una consulta optimizada utilizaría CTEs para pre-filtrar y agregar datos en etapas lógicas, evitando subconsultas correlacionadas. El uso de `SUM() OVER (PARTITION BY ...)` sería clave para cálculos eficientes sin auto-joins costosos. El informe también debería sugerir un índice compuesto en las columnas de `sensor_id`, `timestamp` y `data_type`.",
                            "key_learnings": [
                                "Optimización de consultas SQL avanzadas.",
                                "Uso de CTEs y Window Functions.",
                                "Análisis de planes de ejecución de consulta."
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
