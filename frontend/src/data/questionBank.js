export const questionBank = [
  // TECNOLÓGICAS Y DE INGENIERÍA
  {
    id: 1,
    text: "Al enfrentar un error complejo en un sistema de software o maquinaria, ¿cuál es tu primera reacción?",
    options: [
      { text: "Aislar las variables y revisar los registros (logs) analíticamente.", weights: { analytical: 10, hands_on: 2 } },
      { text: "Preguntar a mis colegas o buscar en foros de la comunidad.", weights: { social: 10, linguistic: 3 } },
      { text: "Probar diferentes enfoques creativos para ver si alguno soluciona el problema.", weights: { creative: 8, hands_on: 5 } },
      { text: "Leer la documentación técnica exhaustivamente.", weights: { linguistic: 8, analytical: 5 } },
      { text: "Desarmar el equipo o reiniciar los servicios manualmente para ver qué ocurre.", weights: { hands_on: 10, creative: 2 } }
    ]
  },
  {
    id: 2,
    text: "Si te piden optimizar un proceso industrial, tú prefieres:",
    options: [
      { text: "Crear un modelo matemático que demuestre la eficiencia.", weights: { analytical: 10 } },
      { text: "Hacer un diseño visual del nuevo flujo de trabajo.", weights: { creative: 10, analytical: 2 } },
      { text: "Capacitar a los operadores sobre el nuevo proceso.", weights: { social: 8, linguistic: 5 } },
      { text: "Escribir el manual de procedimientos detallado.", weights: { linguistic: 10, analytical: 2 } },
      { text: "Modificar la maquinaria físicamente en el piso de fábrica.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 3,
    text: "¿Qué herramienta tecnológica prefieres usar en tu día a día?",
    options: [
      { text: "Hojas de cálculo y bases de datos (Excel, SQL).", weights: { analytical: 10 } },
      { text: "Programas de diseño y modelado (Figma, Blender).", weights: { creative: 10 } },
      { text: "Redes sociales y plataformas de videoconferencia.", weights: { social: 10 } },
      { text: "Procesadores de texto y herramientas de publicación.", weights: { linguistic: 10 } },
      { text: "Simuladores de hardware, robótica o herramientas físicas.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 4,
    text: "En un proyecto de desarrollo de un videojuego, tú preferirías:",
    options: [
      { text: "Programar la inteligencia artificial de los enemigos.", weights: { analytical: 10, creative: 2 } },
      { text: "Diseñar los escenarios, personajes y la paleta de colores.", weights: { creative: 10 } },
      { text: "Gestionar a la comunidad de jugadores y el marketing.", weights: { social: 10, linguistic: 3 } },
      { text: "Escribir el guion, los diálogos y la historia principal.", weights: { linguistic: 10, creative: 5 } },
      { text: "Construir los controles físicos o el hardware para jugar.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 5,
    text: "Si tuvieras que organizar un hackathon, te encargarías de:",
    options: [
      { text: "Definir las métricas de evaluación de los proyectos.", weights: { analytical: 10 } },
      { text: "Diseñar la identidad visual y los pósters del evento.", weights: { creative: 10 } },
      { text: "Hacer networking para conseguir patrocinadores y mentores.", weights: { social: 10 } },
      { text: "Redactar las bases del concurso y las notas de prensa.", weights: { linguistic: 10 } },
      { text: "Montar la infraestructura de red y los servidores físicos.", weights: { hands_on: 10 } }
    ]
  },

  // CORPORATIVAS Y DE NEGOCIOS
  {
    id: 6,
    text: "En una reunión de junta directiva tensa por bajos resultados, tú sueles:",
    options: [
      { text: "Pedir que se muestren los datos reales de ventas para analizar tendencias.", weights: { analytical: 10 } },
      { text: "Proponer una campaña de marketing radicalmente distinta.", weights: { creative: 10, social: 3 } },
      { text: "Mediar entre las partes para bajar la tensión y buscar consenso.", weights: { social: 10 } },
      { text: "Articular un discurso persuasivo para calmar a los inversores.", weights: { linguistic: 10, social: 5 } },
      { text: "Salir a la calle de inmediato a ejecutar pruebas piloto de ventas.", weights: { hands_on: 10, analytical: 2 } }
    ]
  },
  {
    id: 7,
    text: "Al evaluar la viabilidad de un nuevo negocio, tu enfoque es:",
    options: [
      { text: "Hacer un modelo de proyección financiera a 5 años.", weights: { analytical: 10 } },
      { text: "Idear un producto disruptivo que no exista en el mercado.", weights: { creative: 10 } },
      { text: "Construir un equipo fundador sólido y cohesionado.", weights: { social: 10 } },
      { text: "Escribir un plan de negocios cautivador para atraer inversores.", weights: { linguistic: 10, creative: 2 } },
      { text: "Construir un MVP (Producto Mínimo Viable) tangible rápidamente.", weights: { hands_on: 10, creative: 3 } }
    ]
  },
  {
    id: 8,
    text: "Para convencer a un cliente difícil de comprar tu producto, tú:",
    options: [
      { text: "Le muestras un cuadro comparativo de ROI y estadísticas.", weights: { analytical: 10 } },
      { text: "Le presentas una demo visualmente impactante y moderna.", weights: { creative: 10 } },
      { text: "Lo invitas a almorzar para construir una relación de confianza.", weights: { social: 10 } },
      { text: "Utilizas técnicas de oratoria persuasiva y storytelling.", weights: { linguistic: 10, social: 3 } },
      { text: "Le das una muestra del producto para que lo pruebe con sus manos.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 9,
    text: "A la hora de liderar un equipo corporativo, tu estilo es:",
    options: [
      { text: "Basado en KPIs, métricas de rendimiento y objetivos claros.", weights: { analytical: 10 } },
      { text: "Fomentar la innovación constante y las lluvias de ideas.", weights: { creative: 10 } },
      { text: "Empático, priorizando el bienestar emocional del equipo.", weights: { social: 10 } },
      { text: "Comunicativo, enviando memos inspiradores y directrices claras.", weights: { linguistic: 10 } },
      { text: "Liderar con el ejemplo, remangándote para hacer el trabajo sucio.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 10,
    text: "Cuando tienes que presentar un reporte trimestral:",
    options: [
      { text: "Incluyes gráficos detallados, porcentajes y pronósticos.", weights: { analytical: 10 } },
      { text: "Diseñas una presentación en PowerPoint con un diseño exquisito.", weights: { creative: 10 } },
      { text: "Organizas un panel interactivo para responder preguntas del público.", weights: { social: 10 } },
      { text: "Te aseguras de que el resumen ejecutivo esté perfectamente redactado.", weights: { linguistic: 10 } },
      { text: "Llevas prototipos físicos de los productos lanzados en el trimestre.", weights: { hands_on: 10 } }
    ]
  },

  // CIENCIAS Y SALUD
  {
    id: 11,
    text: "En un caso médico de diagnóstico difícil, ¿qué harías primero?",
    options: [
      { text: "Analizar detalladamente los resultados de los exámenes de sangre.", weights: { analytical: 10 } },
      { text: "Pensar en diagnósticos alternativos poco comunes.", weights: { creative: 10, analytical: 3 } },
      { text: "Hablar con el paciente y su familia para entender su entorno.", weights: { social: 10 } },
      { text: "Revisar la literatura médica y los historiales de casos similares.", weights: { linguistic: 10, analytical: 4 } },
      { text: "Realizar una exploración física completa al paciente.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 12,
    text: "Si trabajaras en investigación biológica, preferirías:",
    options: [
      { text: "Analizar secuencias genéticas usando algoritmos.", weights: { analytical: 10, hands_on: 2 } },
      { text: "Diseñar nuevos experimentos visualmente intuitivos.", weights: { creative: 10 } },
      { text: "Dirigir un equipo de investigadores internacionales.", weights: { social: 10 } },
      { text: "Escribir artículos científicos para publicarlos en revistas.", weights: { linguistic: 10 } },
      { text: "Manipular muestras microscópicas y cultivar células en el laboratorio.", weights: { hands_on: 10, analytical: 3 } }
    ]
  },
  {
    id: 13,
    text: "Frente a una crisis sanitaria (ej. pandemia), tu rol ideal sería:",
    options: [
      { text: "Modelar matemáticamente la propagación del virus.", weights: { analytical: 10 } },
      { text: "Idear campañas visuales de concientización pública.", weights: { creative: 10 } },
      { text: "Coordinar esfuerzos entre hospitales y autoridades locales.", weights: { social: 10 } },
      { text: "Redactar los protocolos oficiales de salud pública.", weights: { linguistic: 10 } },
      { text: "Administrar vacunas o construir hospitales de campaña.", weights: { hands_on: 10 } }
    ]
  },

  // ARTES, DISEÑO Y LITERATURA
  {
    id: 14,
    text: "Si tuvieras que escribir un libro, este sería sobre:",
    options: [
      { text: "Patrones económicos y teoría de juegos.", weights: { analytical: 10 } },
      { text: "Un mundo de fantasía con especies e idiomas inventados.", weights: { creative: 10, linguistic: 5 } },
      { text: "Biografías y psicología de grandes líderes sociales.", weights: { social: 10, linguistic: 5 } },
      { text: "Poesía o un ensayo sobre el uso del lenguaje.", weights: { linguistic: 10, creative: 4 } },
      { text: "Un manual de carpintería o reparación de motores.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 15,
    text: "Frente a un lienzo en blanco o una sala vacía a punto de ser decorada:",
    options: [
      { text: "Mides las dimensiones para optimizar el espacio geométricamente.", weights: { analytical: 10 } },
      { text: "Imginas combinaciones de colores audaces y poco convencionales.", weights: { creative: 10 } },
      { text: "Piensas en cómo el espacio hará sentir a los visitantes.", weights: { social: 10, creative: 3 } },
      { text: "Escribes una justificación conceptual de lo que vas a plasmar.", weights: { linguistic: 10 } },
      { text: "Empiezas a pintar, martillar o construir sin pensarlo mucho.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 16,
    text: "En la producción de una obra teatral, tú serías:",
    options: [
      { text: "El administrador del presupuesto y logística.", weights: { analytical: 10 } },
      { text: "El director de arte o diseñador de vestuario.", weights: { creative: 10 } },
      { text: "El actor principal interactuando con el público.", weights: { social: 10 } },
      { text: "El guionista que escribe los diálogos.", weights: { linguistic: 10 } },
      { text: "El técnico encargado de armar la escenografía y las luces.", weights: { hands_on: 10 } }
    ]
  },

  // EDUCACIÓN Y COMUNIDAD
  {
    id: 17,
    text: "Si fueras profesor por un día, ¿qué método de enseñanza usarías?",
    options: [
      { text: "Explicar usando estadísticas, gráficos y lógica deductiva.", weights: { analytical: 10 } },
      { text: "Hacer una presentación dinámica llena de dibujos y analogías visuales.", weights: { creative: 10 } },
      { text: "Fomentar el debate grupal y el trabajo en equipo.", weights: { social: 10 } },
      { text: "Dar una charla magistral inspiradora enfocada en las palabras.", weights: { linguistic: 10 } },
      { text: "Llevar a los alumnos a un taller para que aprendan haciendo.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 18,
    text: "En tu comunidad local, decides organizar un evento. Te encargas de:",
    options: [
      { text: "Manejar las finanzas y proyectar los costos.", weights: { analytical: 10 } },
      { text: "Diseñar el concepto temático y la decoración.", weights: { creative: 10 } },
      { text: "Hablar con los vecinos puerta a puerta para invitarlos.", weights: { social: 10 } },
      { text: "Redactar las cartas de solicitud para el municipio.", weights: { linguistic: 10 } },
      { text: "Montar las carpas y cocinar para el evento.", weights: { hands_on: 10 } }
    ]
  },

  // LEGAL, GESTIÓN PÚBLICA Y RESOLUCIÓN DE CONFLICTOS
  {
    id: 19,
    text: "Frente a un conflicto legal complejo, tu estrategia es:",
    options: [
      { text: "Analizar meticulosamente cada cláusula del contrato en disputa.", weights: { analytical: 10 } },
      { text: "Proponer una solución alternativa (fuera de la caja) que nadie pensó.", weights: { creative: 10 } },
      { text: "Mediar entre ambas partes para encontrar un acuerdo pacífico.", weights: { social: 10 } },
      { text: "Argumentar de manera elocuente frente a un juez o jurado.", weights: { linguistic: 10 } },
      { text: "Ir al lugar de los hechos a recolectar pruebas físicas.", weights: { hands_on: 10, analytical: 3 } }
    ]
  },
  {
    id: 20,
    text: "Si estuvieras redactando una nueva ley o política pública, te enfocarías en:",
    options: [
      { text: "Los datos económicos que respaldan el impacto de la ley.", weights: { analytical: 10 } },
      { text: "Incluir soluciones innovadoras a problemas sociales antiguos.", weights: { creative: 10 } },
      { text: "Asegurarte de que beneficia a los grupos más vulnerables.", weights: { social: 10 } },
      { text: "El uso cuidadoso del lenguaje para evitar ambigüedades legales.", weights: { linguistic: 10, analytical: 3 } },
      { text: "Supervisar la implementación física de las obras públicas relacionadas.", weights: { hands_on: 10 } }
    ]
  },

  // SITUACIONES DE ESTRÉS O COTIDIANAS
  {
    id: 21,
    text: "Cuando te vas de viaje a una ciudad desconocida, tú:",
    options: [
      { text: "Creas un itinerario en Excel con tiempos y presupuestos exactos.", weights: { analytical: 10 } },
      { text: "Buscas lugares únicos para tomar fotos y experimentar arte local.", weights: { creative: 10 } },
      { text: "Te alojas en hostales para conocer gente nueva de todo el mundo.", weights: { social: 10 } },
      { text: "Lees sobre la historia del lugar y escribes un diario de viaje.", weights: { linguistic: 10 } },
      { text: "Haces senderismo intenso o rentas una moto para explorar libremente.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 22,
    text: "En un escape room (habitación de escape), tú eres quien:",
    options: [
      { text: "Resuelve los rompecabezas matemáticos y de secuencias lógicas.", weights: { analytical: 10 } },
      { text: "Encuentra conexiones visuales entre los objetos de la sala.", weights: { creative: 10 } },
      { text: "Mantiene al equipo calmado y coordinado bajo presión.", weights: { social: 10 } },
      { text: "Lee y descifra rápidamente los pergaminos y acertijos escritos.", weights: { linguistic: 10 } },
      { text: "Mueve los muebles y busca compartimentos secretos manipulando cosas.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 23,
    text: "Si te regalan una planta exótica que empieza a marchitarse:",
    options: [
      { text: "Mides la humedad de la tierra y calculas la exposición a la luz solar.", weights: { analytical: 10 } },
      { text: "Le haces una poda decorativa para intentar revitalizarla.", weights: { creative: 10, hands_on: 3 } },
      { text: "Preguntas a tus amigos jardineros o entras a un foro de plantas.", weights: { social: 10 } },
      { text: "Lees un libro o artículos botánicos sobre la especie.", weights: { linguistic: 10 } },
      { text: "La trasplantas inmediatamente a una maceta nueva con diferente abono.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 24,
    text: "A la hora de comprar un producto electrónico nuevo (ej. un teléfono):",
    options: [
      { text: "Comparas las especificaciones técnicas (RAM, procesador) con tablas de rendimiento.", weights: { analytical: 10 } },
      { text: "Te guías por el diseño estético, el color y la belleza de su interfaz.", weights: { creative: 10 } },
      { text: "Pides recomendaciones a tus amigos y conocidos antes de decidir.", weights: { social: 10 } },
      { text: "Lees reseñas detalladas y foros de discusión profunda.", weights: { linguistic: 10 } },
      { text: "Vas a la tienda a tocarlo, probar el peso y sentir los materiales.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 25,
    text: "Si tuvieras que sobrevivir en una isla desierta, tu aporte principal sería:",
    options: [
      { text: "Racionar la comida y calcular la trayectoria de rescate.", weights: { analytical: 10 } },
      { text: "Inventar formas creativas de recolectar agua o hacer señales.", weights: { creative: 10 } },
      { text: "Mantener la moral del grupo alta y evitar conflictos internos.", weights: { social: 10 } },
      { text: "Mantener un registro escrito detallado de los días y sucesos.", weights: { linguistic: 10 } },
      { text: "Construir refugios, hacer fuego y pescar con herramientas improvisadas.", weights: { hands_on: 10 } }
    ]
  },

  // FILOSÓFICAS Y ABSTRACTAS
  {
    id: 26,
    text: "¿Cuál de estas actividades te parece más satisfactoria?",
    options: [
      { text: "Encontrar la solución a un problema lógico que te tomó días.", weights: { analytical: 10 } },
      { text: "Ver terminada una obra de arte o diseño que ideaste desde cero.", weights: { creative: 10 } },
      { text: "Tener una conversación profunda que cambia la vida de un amigo.", weights: { social: 10 } },
      { text: "Terminar de escribir un poema, ensayo o historia emotiva.", weights: { linguistic: 10 } },
      { text: "Arreglar con tus propias manos el motor de un coche averiado.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 27,
    text: "¿Qué asignatura de la escuela te hubiera gustado que fuera más profunda?",
    options: [
      { text: "Matemáticas y Física.", weights: { analytical: 10 } },
      { text: "Artes plásticas y Música.", weights: { creative: 10 } },
      { text: "Psicología y Sociología.", weights: { social: 10 } },
      { text: "Literatura y Filosofía.", weights: { linguistic: 10 } },
      { text: "Taller técnico, Carpintería o Robótica.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 28,
    text: "Cuando juegas a videojuegos de estrategia o rol, ¿qué perfil sueles adoptar?",
    options: [
      { text: "El estratega que optimiza recursos y maximiza las estadísticas.", weights: { analytical: 10 } },
      { text: "El que personaliza al máximo la apariencia del personaje y su casa.", weights: { creative: 10 } },
      { text: "El líder del clan que recluta jugadores y coordina ataques grupales.", weights: { social: 10 } },
      { text: "El que lee todo el 'lore' (historia) y habla con cada NPC (personaje).", weights: { linguistic: 10 } },
      { text: "El artesano que se dedica a farmear materiales y craftear (crear) objetos.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 29,
    text: "Imagina que puedes aprender un superpoder al instante. Elegirías:",
    options: [
      { text: "Tener una capacidad de cálculo sobrehumana e infalible.", weights: { analytical: 10 } },
      { text: "Poder materializar en la realidad cualquier cosa que imagines.", weights: { creative: 10 } },
      { text: "Poder leer las emociones y conectar mentalmente con las personas.", weights: { social: 10 } },
      { text: "Hablar y entender fluidamente todos los idiomas del universo.", weights: { linguistic: 10 } },
      { text: "Tener una agilidad y fuerza físicas ilimitadas para construir montañas.", weights: { hands_on: 10 } }
    ]
  },
  {
    id: 30,
    text: "Finalmente, si tuvieras que describir tu mente, dirías que es como:",
    options: [
      { text: "Una supercomputadora que procesa datos y probabilidades fríamente.", weights: { analytical: 10 } },
      { text: "Un caleidoscopio lleno de colores, ideas abstractas y formas nuevas.", weights: { creative: 10 } },
      { text: "Un tejido interconectado que se alimenta de la energía de otras personas.", weights: { social: 10 } },
      { text: "Una inmensa biblioteca llena de palabras, discursos y metáforas.", weights: { linguistic: 10 } },
      { text: "Un taller lleno de herramientas listas para ensamblar la realidad.", weights: { hands_on: 10 } }
    ]
  }
];

// Helper para barajar preguntas (algoritmo de Fisher-Yates)
export const shuffleQuestions = (array) => {
  const newArr = [...array];
  for (let i = newArr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArr[i], newArr[j]] = [newArr[j], newArr[i]];
  }
  return newArr;
};
