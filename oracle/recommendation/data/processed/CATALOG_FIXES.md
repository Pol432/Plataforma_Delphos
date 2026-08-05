# Correcciones manuales a `simulation_catalog.csv`

Registro de filas editadas a mano sobre el catálogo generado. Si el catálogo se
regenera desde el pipeline, estas correcciones se pierden y hay que reaplicarlas
(o arreglarlas en el origen).

| Fecha | Fila | Qué estaba mal | Qué se corrigió |
|---|---|---|---|
| 2026-08-04 | `sim_database_designer` | Clasificada como `Design` / `Creative & Design` con skills de diseño gráfico (`Research`, `Visual Design`, `Adobe Creative Suite`). Un perfil creativo (Visual Design + Adobe CS) la recibía como recomendación #1, empatada en 0.6442 con `sim_artist`, por encima de `sim_graphic_designer`. Muy probablemente un falso positivo del pipeline por el token "designer" en `base_career`. | `categoria` → `STEM`, `industria` → `Technology` (el resto del catálogo empareja STEM↔Technology 20/20), y skills → `['SQL', 'MongoDB', 'Data Analysis', 'Requirements Gathering']`. Tras el cambio cae al puesto 7 en un perfil analítico (0.6052, matchea SQL + Data Analysis) y desaparece del top-3 creativo. |

Sin cambios en `simulation_id`, `simulation_title`, `nivel_dificultad`,
`duracion_horas` ni `base_career`.

> **Nota para Paúl — divergencia con el dataset de entrenamiento.**
> Solo se tocó `simulation_catalog.csv`, que es lo único que lee el endpoint
> (`backend/app/services/oracle_catalog.py`). `unified_training_dataset_v3.csv`
> mantiene sus 287 filas de `sim_database_designer` como `Design` /
> `Creative & Design`, y los `.npy` no se regeneraron.
>
> Para el bridge heurístico actual da igual (no usa el modelo). Pero cuando entre
> el Wide&Deep detrás de la misma interfaz, esta fila se featurizará en inferencia
> como `STEM`/`Technology` mientras el modelo la vio como `Design`/`Creative & Design`
> en entrenamiento: skew train/serve para esa simulación. Lo correcto sería
> corregirlo en el pipeline de origen y reentrenar, no aquí.
>
> Verificado tras el cambio: `pytest tests/oracle tests/ml_engine` en el backend
> pasa (17 passed); ningún test lee `simulation_catalog.csv` directamente.
