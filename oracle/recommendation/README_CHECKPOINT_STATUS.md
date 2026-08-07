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

**Estado: documentado, sin arreglar.** Desde el cableado del 2026-08-06 el
endpoint SÍ usa este checkpoint, pero sigue sin ser bloqueante: el modelo sólo
decide el orden y su probabilidad cruda no se publica, justamente porque la
calibración no está resuelta. Ver la sección "Cableado al endpoint" al final.

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

**Estado: decidido e IMPLEMENTADO el 2026-08-06.** Ver "Cuándo se aplica" al
final de esta sección.

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

~~**Hoy esto no afecta a nada en producción.**~~ Desactualizado: desde el
cableado del 2026-08-06 el endpoint corre con el Wide&Deep, así que el problema
sí mordía. `GET /oracle/skills` sigue devolviendo 68 nombres (52 + 16), porque
los 16 conservan su entrada en el vocabulario aunque ahora apunten al ID de su
equivalente. Ver la addenda del 2026-08-07 al final de esta sección.

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

**Implementado el 2026-08-06** en `inference.py::_skill_multihot()`, en un commit
propio, previo al cableado del modelo al endpoint.

Detalle de implementación que importa: la tabla `OOV_SKILL_FALLBACKS` está
indexada **por nombre de skill, no por ID sintético**. Los IDs ≥1000 no son
estables — `oracle_catalog._build_skill_vocabulary` los asigna como
`1000 + posición alfabética` sobre el conjunto de nombres desconocidos, así que
si el catálogo gana o pierde un skill todos los posteriores se desplazan. El
featurizador reconstruye esa misma asignación desde los CSV
(`WideDeepFeaturizer._build_oov_map`) y la compone con la tabla de nombres. Una
tabla con 1000..1015 hardcodeados habría empezado a mapear al skill equivocado
en silencio en cuanto el catálogo cambiara.

Los skills mapeados siguen reportándose en `FeaturizationReport.oov_*`, y además
en `FeaturizationReport.mapped_skill_ids` con su destino. Un ID sintético sin
equivalencia decidida se sigue descartando: no se inventa un fallback.

Efecto verificado sobre las 64 simulaciones: 225 → 230 slots activos en total,
la tabla de arriba se reproduce exactamente, y **ninguna simulación queda con 0
slots**. Cubierto por `tests/test_inference.py::TestOutOfVocabularySkills`.

### Addenda 2026-08-07 — el mapeo se extendió al heurístico

Aplicarlo sólo del lado del modelo dejó a los dos motores leyendo el mismo
catálogo de forma distinta, y se notaba en la respuesta al cliente:

```
"simulation_id": "sim_ux_designer",   <-- puesto #1, lo subió el modelo
"matched_skills": [],                 <-- lo llenó el heurístico
"skill_overlap_score": 0.0
```

El featurizador veía la simulación con sus skills traducidos y la rankeaba
primera; `oracle_catalog` seguía viéndola con IDs sintéticos sin resolver y le
calculaba solapamiento 0. La recomendación principal llegaba al frontend sin un
solo skill en común.

Desde el 2026-08-07 `oracle_catalog._build_skill_vocabulary` aplica la **misma**
tabla, importada de `inference.py` — no copiada, porque dos copias se
desincronizan. Se mapean los dos lados (skills de simulación y del usuario),
igual que hace `_skill_multihot`.

Consecuencias medidas:

| | Antes | Después |
|---|---|---|
| `sim_ux_designer.simulation_skill_ids` | `[1004,1012,1013,1014,1015]` | `[17,38,39]` |
| IDs sintéticos que sobreviven en el catálogo | 16 | **0** |
| `resolve_skill_names(["Figma"])` | `[1004]` | `[39]` |
| `unresolved_skill_names(["Figma"])` | `[]` | `[]` (sin cambio) |

Dos cosas que esto **sí** cambia y conviene tener presentes:

1. **Los `scores` de 6 de las 64 simulaciones se mueven**, en los dos motores
   —incluido `ORACLE_ENGINE=heuristic`—, porque `skill_overlap_score` alimenta
   `engagement_probability`. La *forma* de la respuesta no cambia; los valores
   sí.
2. **Quien escriba "Figma" verá "Adobe Creative Suite"** en `matched_skills`.
   Es el precio de la simetría con el modelo, que mapea los dos bloques.

Dos detalles de implementación que no son obvios:

* El offset sintético se sigue calculando sobre **todos** los nombres
  desconocidos, mapeados o no. `_build_oov_map` reconstruye esa numeración por
  su cuenta; si el catálogo se saltara los mapeados al enumerar, las dos
  asignaciones se desalinearían y el featurizador mapearía al skill equivocado
  en silencio.
* Si `oracle/recommendation/` no está disponible, el import falla, se registra
  un warning y el catálogo **degrada al comportamiento anterior** (IDs
  sintéticos) en vez de romper. `oracle_catalog` sirve todas las peticiones,
  incluidas las del kill switch: no puede quedar rehén de la carpeta del
  modelo.

Cubierto por
`backend/tests/oracle/test_oracle_engine_selection.py::TestOovMappingCoherence`.

---

## 2026-08-06 — Confirmación: train/serve skew de `sim_database_designer`

**Estado: el DATASET quedó corregido el 2026-08-06 (ver addenda al final de esta
sección). El SKEW SIGUE VIVO** — está en los pesos del checkpoint, no en el CSV.

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

### Addenda 2026-08-06 — dataset de entrenamiento corregido

Se corrigieron las 287 filas, en las **dos** mitades (los skills no viven en el
CSV, viven en el `.npy` indexado por fila — corregir sólo el CSV habría dejado
la mitad del desfase):

| Artefacto | Campo | Antes | Después |
|---|---|---|---|
| `unified_training_dataset_v3.csv` | `simulation_categoria` (+`_encoded`) | `Design` (1) | `STEM` (7) |
| `unified_training_dataset_v3.csv` | `simulation_industria` (+`_encoded`) | `Creative & Design` (1) | `Technology` (7) |
| `simulation_skill_vectors.npy` | vector de skills | `['Research']` | `['SQL','MongoDB','Data Analysis','Requirements Gathering']` |

Sin cambios en `label`, `engagement_probability`, `nivel_dificultad`,
`duracion_horas` ni en `user_skill_vectors.npy`. El diff toca exactamente 287
líneas y 287 vectores, nada más. Dataset y catálogo de serving ya coinciden para
esta fila.

**Esto NO elimina el skew, y es importante no leerlo como que sí.** El
checkpoint ya está entrenado: sus pesos vieron `Design`/`Creative & Design`.
Corregir el dataset alinea el *registro* con el catálogo, pero el modelo sigue
puntuando esa simulación con lo que aprendió. El skew sólo desaparece
reentrenando.

**Efecto sobre las métricas reproducidas.** 94 de las 287 filas caen en el split
de test, así que los números de la sección "Métricas reproducidas localmente"
dejan de reproducirse tal cual:

| Métrica | Dataset anterior | Dataset corregido |
|---|---|---|
| AUC-ROC (n=3584) | 0.776371 | **0.776250** |
| Accuracy @0.65 | 83.6496 % | **84.1797 %** |

El AUC baja 0.0001 y la accuracy sube 0.53 pp. La diferencia es despreciable,
pero si alguien reevalúa y no obtiene 0.776371, ésta es la razón — no una
regresión.

---

## 2026-08-06 — La suite se valida contra PostgreSQL real

Hasta hoy la suite del backend corría siempre sobre SQLite: `tests/conftest.py`
tenía la URL hardcodeada, así que ejecutarla dentro del contenedor tampoco la
llevaba a Postgres. Ahora acepta `TEST_DATABASE_URL` (SQLite sigue siendo el
default):

    docker compose exec \
      -e TEST_DATABASE_URL=postgresql://postgres:postgres@db:5432/aurum_test \
      web pytest

**Resultado: 408 passed, 19 skipped, 0 failed** en ambos motores.

Habilitarlo destapó 2 tests que sólo pasaban por artefactos de SQLite —
comparación de datetimes naive contra columnas `DateTime(timezone=True)`, y un
id de usuario fijo que daba por hecho que las secuencias vuelven atrás con el
rollback (en PostgreSQL no: `nextval` no es transaccional). Ninguno era un
fallo de la aplicación, pero el segundo hacía que un test de autorización
recibiera 404 y nunca ejerciera la regla que dice cubrir. Ambos corregidos.

Relevante para el oráculo: el flujo `[0]-[6]` de la demo se verificó de punta a
punta contra este mismo stack (Postgres + `delphos_api`), con resultados
idénticos a los de SQLite — `catalog_size=64`, vocabulario de 68 skills,
`engine=heuristic_bridge_v1`. Las decisiones de datos registradas arriba no
cambian con el motor real.

---

## 2026-08-06 — Cableado al endpoint `/api/v1/oracle/recommend`

El Wide&Deep ya no está desconectado: `POST /api/v1/oracle/recommend` lo usa.
Verificado de punta a punta contra el usuario demo (`user_id` 134) sobre el
stack real (Postgres + `delphos_api`).

### Qué hace exactamente el modelo — y qué NO hace

**El modelo sólo decide el ORDEN de la lista.** Los valores de `scores`
(`engagement_probability`, `skill_overlap_score`, `difficulty_match_score`,
`label`, `confidence_interval`) los sigue produciendo `heuristic_bridge_v1`,
exactamente como antes.

La probabilidad cruda del modelo **no se publica**. Motivo: la calibración está
sin resolver (AUC 0.9928 train / 0.7740 test; 85.6 % de las probabilidades fuera
de [0.01, 0.99]; un 25 % son exactamente 0.0 por underflow de sigmoid).
Publicarla en un campo llamado `engagement_probability` la presentaría como algo
que no es, y mostraría "0 %" en varias tarjetas de la demo. El orden relativo,
en cambio, sí es utilizable: AUC 0.7764.

**Consecuencia visible que conviene conocer:** como el orden lo pone el modelo y
el número lo pone el heurístico, la lista devuelta **no está ordenada de forma
monótona por `engagement_probability`**. En la validación, el #2 mostraba 0.4155
y el #3, 0.6058. No es un bug. Si el frontend asume monotonía para algo (barras,
"score decreciente"), hay que mirarlo.

El orden viene de `inference.py::rank_candidates()`: probabilidad primero y, en
los empates de la cola saturada, desempate por solapamiento de skills y luego
alineación de dificultad. No se desempata con el logit a propósito (AUC 0.2129
dentro de la cola, peor que el azar).

### El contrato JSON no cambia

Mismos campos y mismo shape en los dos caminos. Lo único que cambia es `engine`,
que refleja **qué motor ordenó de verdad** — sin eso, un fallback silencioso
sería indistinguible de un modelo funcionando, que es justo lo que había que
poder comprobar. Cubierto por
`backend/tests/oracle/test_oracle_engine_selection.py::TestEndpointContract`.

### Motor y fallback (`app/services/oracle_engine.py`)

`ORACLE_ENGINE` controla el motor:

| Valor | Comportamiento |
|---|---|
| `auto` (default) | Intenta el Wide&Deep; cae al heurístico ante cualquier problema. |
| `heuristic` | Kill switch. Ni siquiera importa MindSpore. Apaga el modelo sin redeploy. |
| `widedeep` | Exige el modelo y propaga los errores. Para tests y diagnóstico. |

En `auto` se cae al heurístico si: el modelo no carga (falta MindSpore, falta el
checkpoint, no encaja con la arquitectura), la inferencia lanza una excepción, o
la salida es **degenerada**. Degenerada = las 64 con el mismo score, todas
saturadas en el mismo extremo, o algún NaN/infinito. Que *muchas* empaten a 0.0
NO es degenerado: es el comportamiento conocido del checkpoint y
`rank_candidates()` lo desempata; sólo se rechaza si empata el catálogo entero.

Un fallo de carga se recuerda y no se reintenta por petición — si no, un problema
de arranque se convertiría en un timeout en cada request.

### Despliegue

* `mindspore==2.6.0`, `numpy<2` y `scikit-learn~=1.3.0` entran en
  `backend/requirements.txt`. La imagen es `python:3.11-slim` y MindSpore 2.6.0
  publica wheel `cp311`. La imagen pasa de ~565 MB a ~3.45 GB.
* `docker-compose.yml` monta `../oracle/recommendation:/opt/oracle:ro` y define
  `ORACLE_MODEL_DIR`. El montaje anterior de `data/processed` se mantiene:
  `oracle_catalog` usa su propia variable y no tiene por qué saber del modelo.
* Si las dependencias faltan, el endpoint **sigue funcionando**: cae al
  heurístico. No es un despliegue de todo-o-nada.

### Validación end-to-end (usuario demo, `user_id` 134)

Mismo perfil, antes y después:

| # | Antes (`heuristic_bridge_v1`) | Después (`wide_and_deep`) |
|---|---|---|
| 1 | `sim_artist` | `sim_artist` |
| 2 | `sim_embedded_systems_engineer` | `sim_ux_designer` |
| 3 | `sim_automation_engineer` | `sim_graphic_designer` |
| 4 | `sim_nlp_engineer` | `sim_fashion_designer` |
| 5 | `sim_front-end_developer` | `sim_database_designer` |

**9 de 10 posiciones cambian** — el modelo se está usando de verdad, no se está
ignorando en silencio. El shape de la respuesta es idéntico y los `scores` de
cada simulación coinciden exactamente entre ambas ejecuciones, como debe ser.

`sim_ux_designer` en el puesto #2 es evidencia directa del mapeo de skills OOV:
con 0 slots activos no podía llegar ahí.

Fallbacks probados con fallos reales, no simulados:

| Escenario | Resultado |
|---|---|
| Checkpoint retirado del disco | HTTP 200, `heuristic_bridge_v1`, aviso en log |
| `ORACLE_ENGINE=heuristic` | HTTP 200, `heuristic_bridge_v1` |
| Todo en su sitio | HTTP 200, `wide_and_deep` |

Latencia: ~3 s la primera petición (construye el grafo de MindSpore una vez),
~18 ms las siguientes.

Suites: **436 passed / 19 skipped** en el backend, **56 passed** en
`oracle/recommendation`.

### Lo que sigue abierto

* La calibración (sección "RIESGO ABIERTO"). Mitigada, no resuelta: se evita
  publicar la probabilidad, pero el modelo sigue generalizando a 0.77.
* El skew de `sim_database_designer` en los pesos, y la paridad train/serve que
  el mapeo de OOV rompe a propósito. Las dos se cierran reentrenando.
