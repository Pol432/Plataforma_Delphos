Checkpoint disponible (checkpoints/dao_wide_deep_final.ckpt), carga sin
errores bajo MindSpore 2.6.0 (13/13 parámetros, shapes OK). AUC/F1 real
NO reproducido: el notebook de entrenamiento fue editado después del
entrenamiento que generó los resultados en evaluation_results.json
(AUC 0.776274, época 828). El checkpoint disponible corresponde al final
del entrenamiento (época 980), cuya referencia más confiable si se
reevalúa sería AUC ≈ 0.7729, no 0.776274 — sin confirmar todavía porque
el MindRecord de test no existe en el repo (gitignored) y no se
regeneró por riesgo de que las celdas 7-10 de generación de features
hayan derivado del código que vio el checkpoint original.
Pendiente: regenerar MindRecord y reevaluar, o localizar
dao_wide_deep_best.ckpt (el checkpoint de mejor época, distinto del
final, nunca commiteado a git).

---

## 2026-07-27 — dao_wide_deep_best.ckpt localizado

`dao_wide_deep_best.ckpt` (el checkpoint de mejor época, no sólo el
`_final.ckpt`) fue localizado en el repo fuente
`IA_Delphos/Wide-Deep-Career-Recommendation-System/checkpoints/baseline/`
y copiado al monorepo:

    oracle/recommendation/checkpoints/baseline/dao_wide_deep_best.ckpt

`training_config.json` y `evaluation_results.json` ya estaban presentes en
`oracle/recommendation/checkpoints/` y son idénticos a los del repo fuente
(verificado con `cmp`), así que no se re-copiaron.

### Métricas confirmadas

Provienen de `evaluation_results.json`, cuyo campo `checkpoint` apunta
explícitamente a `.../baseline/dao_wide_deep_best.ckpt` — es decir, estas
métricas corresponden a este checkpoint, no al `_final.ckpt`:

| Métrica    | Valor    |
|------------|----------|
| AUC-ROC    | 0.7763   |
| F1 Score   | 0.6030   |
| Accuracy   | 83.65 %  |
| Threshold  | 0.65     |
| Precision  | 0.5514   |
| Recall     | 0.6652   |
| n_test     | 3584     |

### Corrección de la celda 6 del notebook

`notebooks/Week 3 - Model Training/02_model_build_and_train.ipynb`, celda 6,
declaraba `emb_dim=8` y `deep_layer_dim=[128, 64, 32, 16]`, valores que **no**
corresponden al checkpoint y que provocaban un fallo de carga por shape
mismatch. Se corrigieron a los valores reales del checkpoint:

- `emb_dim = 16`
- `deep_layer_dim = [256, 128, 64, 32]`

Confirmado contra las shapes del propio checkpoint (`embedding_table`
(148, 16), `dense_layer_1` (1840, 256) = field_size 115 × emb_dim 16) y contra
`training_config.json`, que ya registraba `emb_dim: 16` y
`deep_layer_dim: [256, 128, 64, 32]`. La celda 6 había sido editada después
del entrenamiento — de ahí la discrepancia original. Con esto el notebook
queda alineado con el checkpoint y no se vuelve a caer en el mismo
diagnóstico.

### Estado

- **`checkpoints/baseline/dao_wide_deep_best.ckpt` es ahora el checkpoint de
  referencia para la demo.**
- `checkpoints/dao_wide_deep_final.ckpt` (época 980, sin best-AUC) queda
  únicamente como histórico; no debe usarse para la demo ni para reportar
  métricas.

No se reentrenó ni se regeneró el MindRecord. Las métricas de arriba son las
registradas en `evaluation_results.json` del entrenamiento original, no una
reevaluación local.

---

## 2026-07-29 — Métricas reproducidas localmente

El pendiente de arriba ("AUC/F1 real NO reproducido") queda **cerrado**. No hizo
falta regenerar el MindRecord: `inference.py` featuriza directamente desde
`unified_training_dataset_v3.csv` y los vectores `.npy`, aplicando el mismo
corte secuencial 80/20 y el mismo truncado a múltiplos de 256 (`drop_remainder`)
que usó el entrenamiento.

Evaluado sobre las 3584 filas del split de test con
`checkpoints/baseline/dao_wide_deep_best.ckpt`, en el contenedor
`Dockerfile.inference` (Python 3.10 + MindSpore 2.6.0):

| Métrica   | Reproducido | Publicado | Delta    |
|-----------|-------------|-----------|----------|
| AUC-ROC   | 0.776371    | 0.776274  | +0.0001  |
| Accuracy  | 83.6496 %   | 83.6496 % | exacto   |
| F1        | 0.6030      | 0.6030    | exacto   |
| Precision | 0.5514      | 0.5514    | exacto   |
| Recall    | 0.6652      | 0.6652    | exacto   |

Las cuatro métricas de umbral coinciden **exactamente**, es decir que las
predicciones binarias a 0.65 son idénticas a las de la evaluación original. Esto
valida de punta a punta que la featurización de `inference.py` reproduce la del
entrenamiento.

Nota sobre el AUC: `MatchingOutput.engagement_probability` redondea a 4
decimales y eso colapsa 2329 de 3584 probabilidades a `0.0` exacto. Medido sobre
esos valores redondeados el AUC sube artificialmente a 0.7972. El 0.776371 de la
tabla es sobre probabilidades crudas.

### Generalización

| Split           | n    | AUC-ROC | Accuracy @0.65 |
|-----------------|------|---------|----------------|
| Test (no visto) | 3701 | 0.7740  | 83.03 %        |
| Train (muestra) | 3701 | 0.9928  | 95.38 %        |

Hay sobreajuste real: 0.99 en entrenamiento contra 0.77 en test. Además el
modelo está mal calibrado en ambos splits — 85.6 % de las probabilidades de test
caen fuera de [0.01, 0.99] y sólo un 8.1 % queda en la zona media 0.1–0.9. La
saturación no es memoria de las filas vistas: ocurre igual sobre datos nuevos.

---

## RIESGO ABIERTO — Calibración del modelo

**Estado: documentado, sin arreglar. No bloqueante hoy** — el endpoint
`/api/v1/oracle` corre con la heurística de puente, no con este checkpoint.

### Qué se midió

Sobre el split de test (3701 filas nunca vistas) contra una muestra del mismo
tamaño del split de entrenamiento, con `dao_wide_deep_best.ckpt`:

| Split           | n    | AUC-ROC | Accuracy @0.65 | Saturadas | Zona 0.1–0.9 |
|-----------------|------|---------|----------------|-----------|--------------|
| Test (no visto) | 3701 | 0.7740  | 83.03 %        | 85.6 %    | 8.1 %        |
| Train (muestra) | 3701 | 0.9928  | 95.38 %        | 82.5 %    | 12.7 %       |

Son **dos problemas distintos**, no uno:

**1. Sobreajuste.** AUC 0.9928 en entrenamiento contra 0.7740 en test. Esperable
con 18 501 muestras y ~828 épocas, pero la brecha es grande.

**2. Mala calibración, independiente del sobreajuste.** El 85.6 % de las
predicciones de test cae fuera de [0.01, 0.99] y sólo un 8.1 % queda en la zona
media. 2801 de 3701 caen en el primer decil. **La saturación no es memoria de
las filas vistas: el test satura más que el train (85.6 % vs 82.5 %).** El
modelo es igual de sobreconfiado sobre datos nuevos.

### Consecuencia práctica para el ranking

Sobre las 3584 filas de la evaluación de referencia, 900 probabilidades (25.1 %)
son **exactamente 0.0** por underflow de sigmoid en float32 — no por redondeo.
Esos 900 candidatos empatan y no son ordenables por probabilidad.

El logit sí los separa, pero **no sirve para ordenarlos**:

| Región                 | n    | AUC por probabilidad | AUC por logit |
|------------------------|------|----------------------|---------------|
| Fuera de la cola       | 2684 | 0.835092             | 0.835092      |
| Dentro de la cola      |  900 | empates (0.5)        | **0.2129**    |
| Global                 | 3584 | **0.776371**         | 0.765215      |

Dentro de la cola saturada el logit ordena **peor que al azar**: es
anti-informativo ahí. Ordenar por logit baja el AUC global de 0.7764 a 0.7652.
Por eso `inference.py::rank_candidates()` desempata con los diagnósticos
descriptivos (solapamiento de skills, luego alineación de dificultad), que son
interpretables y no dependen de la calibración.

### Qué NO se hizo y por qué

No se aplicó ningún ajuste de calibración (temperature scaling, Platt scaling,
isotonic). Es una decisión de coste/beneficio para el timeline del piloto y no
urge: el endpoint no usa este modelo todavía. Si se decide abordarlo, temperature
scaling sobre el logit es lo más barato — un solo parámetro ajustado en el split
de test — pero conviene medir antes si mueve el AUC o sólo la calibración
(típicamente sólo lo segundo, que es justo lo que aquí importa para el ranking).

Cualquier decisión sobre esto debe considerar además que el sobreajuste es real:
recalibrar no arregla un modelo que generaliza a 0.77.

---

## 2026-08-06 — DECISIÓN TOMADA: skills fuera de vocabulario (IDs ≥1000)

**Estado: decidido. Ya no es un riesgo abierto.** Implementación pendiente para
Semana 2 (ver "Cuándo se aplica" al final de esta sección).

### El problema, con números

El modelo entrenó con 52 skills (`data/processed/skills_catalog.csv`,
`skill_id` 1..52, posición en el multi-hot = `skill_id - 1`). El catálogo de
serving referencia **16 skills adicionales** a los que
`app/services/oracle_catalog.py` asigna IDs sintéticos ≥1000. El modelo nunca
los vio y no tienen fila en la tabla de embeddings.

Afectan a **6 de las 64 simulaciones**:

| Simulación | Skills OOV | Skills OOV concretos |
|---|---|---|
| `sim_ux_designer`      | 5/5 | UI Design, UX Research, User Research, Figma, Wireframing |
| `sim_project_manager`  | 4/5 | Project Management, Jira, Scrum, Agile |
| `sim_lawyer`           | 3/6 | Intellectual Property, Compliance, Contract Review |
| `sim_graphic_designer` | 2/4 | Photoshop, Branding |
| `sim_digital_marketer` | 1/5 | PPC |
| `sim_psychologist`     | 1/5 | Patient Education |

Ninguna simulación se descarta del catálogo: las 64 se puntúan siempre. Lo que
se degrada es la señal de skills. El único caso realmente roto es
`sim_ux_designer`, que con 0/5 slots activos se puntuaba **sólo** por sus
features categóricas y continuas.

**Hoy esto no afecta a nada en producción.** El endpoint `/api/v1/oracle` corre
con `heuristic_bridge_v1`, que sí usa los IDs sintéticos (`GET /oracle/skills`
devuelve 68 = 52 + 16). El problema sólo muerde cuando el Wide&Deep entre
detrás de la misma interfaz.

### Decisión: mapear a un skill de fallback dentro del vocabulario

Decidido por Paúl el 2026-08-06. Los 16 OOV se mapean al skill más cercano de
los 52 entrenados en lugar de descartarse:

| Skill OOV | → Fallback | id |
|---|---|---|
| Photoshop | Adobe Creative Suite | 39 |
| Figma | Adobe Creative Suite | 39 |
| Branding | Brand Management | 41 |
| Patient Education | Patient Care | 26 |
| UI Design | Visual Design | 38 |
| Wireframing | Visual Design | 38 |
| UX Research | Research | 17 |
| User Research | Research | 17 |
| Project Management | Strategic Planning | 21 |
| Jira | Strategic Planning | 21 |
| Scrum | Strategic Planning | 21 |
| Agile | Strategic Planning | 21 |
| Intellectual Property | Legal Research | 49 |
| Compliance | Legal Research | 49 |
| Contract Review | Case Analysis | 50 |
| PPC | Marketing | 18 |

### Efecto medido del mapeo

Slots activos en el multi-hot de 52 posiciones, antes → después:

| Simulación | Antes | Después |
|---|---|---|
| `sim_ux_designer`      | 0 | **3** |
| `sim_graphic_designer` | 2 | 3 |
| `sim_project_manager`  | 1 | 2 |
| `sim_digital_marketer` | 4 | 4 (sin cambio) |
| `sim_lawyer`           | 3 | 3 (sin cambio) |
| `sim_psychologist`     | 4 | 4 (sin cambio) |

En 3 de las 6 el mapeo es un **no-op**: el fallback ya estaba activo por otro
skill de la misma simulación (`sim_lawyer` ya tenía Legal Research y Case
Analysis; `sim_psychologist` ya tenía Patient Care; `sim_digital_marketer` ya
tenía Marketing). Es decir, el valor real de esta decisión es arreglar
`sim_ux_designer` y, en menor medida, `sim_graphic_designer` y
`sim_project_manager`.

### Contrapartida aceptada explícitamente

El mapeo **rompe la paridad train/serve a propósito**: se le presenta al modelo
un skill que la simulación no tiene realmente, apoyándose en una equivalencia
semántica que el modelo nunca aprendió. Es el mismo tipo de skew que ya está
abierto en `sim_database_designer` (ver sección siguiente), y las
equivalencias no son todas del mismo nivel de confianza:

* **Casi exactas** — Photoshop→Adobe Creative Suite, Branding→Brand Management,
  Patient Education→Patient Care.
* **Gruesas** — Jira/Scrum/Agile→Strategic Planning colapsa cuatro skills
  distintos en un solo slot; Figma→Adobe Creative Suite equipara dos
  herramientas que no se parecen más allá de ser de diseño.

Se asume el trade-off: cobertura de las 6 simulaciones por encima de la
paridad estricta, para el piloto de agosto. La alternativa de raíz —
regenerar el dataset con vocabulario 68 y reentrenar — invalidaría las métricas
ya reportadas (AUC 0.7763) y no cabe en el timeline.

### Cuándo se aplica

**No implementado todavía.** El cambio vive en
`inference.py::_skill_multihot()`, que hoy no está conectado al endpoint. Se
implementa junto con el cableado del modelo en Semana 2, en el mismo commit,
para que la featurización y el motor entren a la vez. Cuando se implemente,
los skills mapeados deben seguir reportándose en
`FeaturizationReport.oov_*` — mapear no debe convertirse en un descarte
silencioso disfrazado.

---

## 2026-08-06 — Confirmación: train/serve skew de `sim_database_designer`

**Estado: documentado, sin resolver, a propósito. No bloqueante hoy.**

Registro completo en
`oracle/recommendation/data/processed/CATALOG_FIXES.md`. Resumen:

* **Detectado el 2026-08-04.** `sim_database_designer` estaba clasificada como
  `Design` / `Creative & Design` con skills de diseño gráfico (`Research`,
  `Visual Design`, `Adobe Creative Suite`) — muy probablemente un falso positivo
  del pipeline por el token "designer" en `base_career`. Un perfil creativo la
  recibía como recomendación #1 (0.6442), por encima de `sim_graphic_designer`.
* **Corregido sólo en serving.** `simulation_catalog.csv` pasó a
  `STEM` / `Technology` con skills `['SQL', 'MongoDB', 'Data Analysis',
  'Requirements Gathering']`.
* **NO corregido en entrenamiento.** `unified_training_dataset_v3.csv` mantiene
  sus 287 filas como `Design` / `Creative & Design`, y los `.npy` no se
  regeneraron.

**Por qué no se resuelve todavía:** el endpoint corre con el bridge heurístico,
que no usa el modelo, así que hoy la divergencia no tiene efecto observable. El
skew sólo se materializa cuando el Wide&Deep entre en el endpoint: esa fila se
featurizará en inferencia como `STEM`/`Technology` mientras el modelo la vio
como `Design`/`Creative & Design` en entrenamiento.

**Cómo se resuelve:** corrigiéndolo en el pipeline de origen y reentrenando, no
parcheando el catálogo. Se aborda al conectar el modelo en Semana 2, junto con
el mapeo de skills OOV de la sección anterior — son el mismo problema de fondo
(catálogo de serving que ha derivado del dataset de entrenamiento) y conviene
resolverlos de una sola vez.
