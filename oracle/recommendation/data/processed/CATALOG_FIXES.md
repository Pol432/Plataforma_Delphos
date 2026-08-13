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
> ~~Solo se tocó `simulation_catalog.csv`~~ **RESUELTO PARCIALMENTE el 2026-08-06.**
>
> El dataset de entrenamiento quedó alineado con el catálogo: las 287 filas de
> `sim_database_designer` en `unified_training_dataset_v3.csv` pasaron a
> `STEM` / `Technology` (con sus columnas `*_encoded`), y sus vectores en
> `simulation_skill_vectors.npy` pasaron de `['Research']` a
> `['SQL','MongoDB','Data Analysis','Requirements Gathering']`.
>
> **El skew train/serve NO desapareció.** Vive en los pesos del checkpoint, que
> se entrenó viendo `Design`/`Creative & Design`. Corregir el dataset alinea el
> registro, no el modelo. Sólo se cierra reentrenando.
>
> Efecto secundario a tener en cuenta: 94 de esas 287 filas caen en el split de
> test, así que las métricas reproducidas pasan de AUC 0.776371 / 83.6496 % a
> 0.776250 / 84.1797 %. Detalle en `README_CHECKPOINT_STATUS.md`.
>
> Verificado tras el cambio: `pytest tests/oracle tests/ml_engine` en el backend
> pasa (17 passed); ningún test lee `simulation_catalog.csv` directamente.
