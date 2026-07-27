# Oracle

Los tres subsistemas de IA de la Plataforma Delphos:

- **recommendation/** — Wide & Deep para recomendación de carreras (MindSpore).
- **learning_path/** — optimizador de rutas de aprendizaje / currículum.
- **skill_graph/** — grafo temporal de habilidades (inferencia y taxonomía).

Por ahora son **independientes**: cada uno tiene su propio `requirements.txt` y se
ejecuta por separado. No están fusionados en un único servicio todavía.
