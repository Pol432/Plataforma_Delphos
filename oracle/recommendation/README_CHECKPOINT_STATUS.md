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
