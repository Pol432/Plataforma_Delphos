# Roadmap de Desarrollo Frontend - Agosto

**Responsable:** Alex
**Objetivo Principal:** Desarrollo y entrega del cliente web (Frontend) de la Plataforma Delphos para finales de agosto.
**Enfoque de Diseño:** Diseño limpio, corporativo y educativo. **Cero gamificación**.

---

## Tareas por Semana

### Semana 1: Rediseño y Bases del Sistema (1 - 7 de Agosto)
- [ ] **Auditoría de UI actual:** Revisar las pantallas existentes en `src/screens/` y eliminar cualquier elemento visual de gamificación (barras de experiencia, monedas, avatares tipo juego, etc.).
- [ ] **Design System Educativo:** Definir e implementar la nueva paleta de colores, tipografías y componentes base (botones, tarjetas, modales) enfocados en un entorno de aprendizaje limpio y profesional.
- [ ] **Refactorización de Layouts:** Ajustar la navegación principal y la estructura base de la aplicación para que refleje el nuevo enfoque.

### Semana 2: Vistas Core y Flujos de Aprendizaje (8 - 14 de Agosto)
- [ ] **Dashboard del Estudiante:** Construir la vista principal del usuario con su progreso educativo de forma clara y minimalista.
- [ ] **Módulo de Recomendación de Carreras:** Crear la interfaz para mostrar los resultados del motor de IA (`oracle/recommendation`), mostrando el porqué de cada sugerencia.
- [ ] **Rutas de Aprendizaje (Learning Paths):** Implementar la visualización del grafo de habilidades y las rutas óptimas generadas por `oracle/learning_path`.

### Semana 3: Módulo de Simulaciones (15 - 21 de Agosto) *[Trabajo Conjunto con Mati]*
- [ ] **Definición de Contratos API:** Reunión con Mati para definir los endpoints, requests y responses del módulo de simulaciones.
- [ ] **Desarrollo de UI de Simulaciones:** Crear las interfaces interactivas donde el usuario ejecutará y visualizará las simulaciones.
- [ ] **Integración Frontend-Backend:** Conectar las pantallas de simulación con los endpoints desarrollados por Mati.
- [ ] **Manejo de Estados y Errores:** Implementar loading states, validaciones y feedback visual durante las simulaciones.

### Semana 4: Pruebas, Pulido y Entrega (22 - 31 de Agosto)
- [ ] **Responsive Design:** Asegurar que todas las vistas (especialmente Simulaciones y Rutas de Aprendizaje) funcionen perfectamente en dispositivos móviles y tablets.
- [ ] **Pruebas End-to-End (E2E):** Probar los flujos completos desde el registro, recomendación, rutas y simulaciones.
- [ ] **Optimización de Rendimiento:** Revisar el bundle con Vite, optimizar carga de imágenes y tiempos de respuesta percibidos.
- [ ] **Congelamiento de Código (Code Freeze):** Resolución de bugs finales y preparación para la entrega de fin de mes.


