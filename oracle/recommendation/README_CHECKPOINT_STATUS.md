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
