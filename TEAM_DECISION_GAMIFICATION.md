# Decisión pendiente: gamificación (Alex ↔ Matías)

El roadmap del frontend pide quitar la gamificación. El backend y varias
pantallas ya construidas están montados sobre ella. Este fichero solo deja
constancia de dónde aparece cada cosa; **no propone ninguna dirección** ni se ha
tocado nada de lo que sigue.

---

## 1. Lo que dice el roadmap

`frontend/ROADMAP_AGOSTO.md:5`

> **Enfoque de Diseño:** Diseño limpio, corporativo y educativo. **Cero gamificación**.

`frontend/ROADMAP_AGOSTO.md:12` (Semana 1)

> **Auditoría de UI actual:** Revisar las pantallas existentes en `src/screens/` y
> eliminar cualquier elemento visual de gamificación (barras de experiencia,
> monedas, avatares tipo juego, etc.).

Autor: Alex (`ALopez0510`), commits `f9e9312` y `b7bb41d`.

---

## 2. Campos de gamificación en el esquema (backend)

### Modelo de usuario — `backend/app/models/user.py`

| Línea | Columna |
|---|---|
| 41 | `xp_total = Column(Integer, default=0, nullable=False)` |
| 42 | `xp_validated = Column(Integer, default=0)` |
| 43 | `level_current = Column(Integer, default=1)` |
| 44 | `streak_days = Column(Integer, default=0)` |

`xp_total` es `nullable=False`.

### Expuestos por la API — `backend/app/schemas/user.py`

| Línea | Campo |
|---|---|
| 83 | `xp_total: int = 0` (en `UserOut`) |
| 84 | `level_current: int = 1` (en `UserOut`) |

Van en la respuesta de `/api/v1/register`, `/api/v1/users/me` y `/api/v1/users`.

### Otros sitios del backend

| Fichero:línea | Qué |
|---|---|
| `backend/app/models/simulations.py:46` | `xp_reward = Column(Integer, default=500)` en `Simulation` |
| `backend/app/models/simulations.py:96` | `xp_reward = Column(Integer, default=50)` en `ModuleTask` |
| `backend/app/models/progress.py:64` | `xp_total` en el modelo de progreso |
| `backend/app/models/progress.py:71-75` | cálculo de nivel: `(nivel ** 2) * 100` |

---

## 3. Gamificación en las pantallas ya construidas (frontend)

### `Screen6Victory.jsx` — pantalla de victoria con confeti

| Línea | Qué |
|---|---|
| 4 | `import ReactConfetti from 'react-confetti'` |
| 9, 21 | estado `confettiDone`, temporizador de 5 s |
| 95-97 | overlay `<ReactConfetti />` |

`react-confetti` es dependencia declarada en `frontend/package.json`.

### `Screen3Dashboard.jsx`

| Línea | Qué |
|---|---|
| 157-159 | estado con `xp_total`, `level_current`, `streak_days` |
| 208-209 | «Nivel N» y «X / 100 XP» |
| 213 | barra de progreso de XP animada |
| 223-228 | indicador de racha con pulso animado («RACHA ACTIVA») |
| 258-260 | tarjetas «XP Total» y «Racha» |

### `Screen8Profile.jsx`

| Línea | Qué |
|---|---|
| 133 | tarjeta «Nivel Actual» con icono `Trophy` |
| 157, 173 | racha con icono `Flame` («N días de racha») |
| 184-185 | «NIVEL N» y «X / 100 XP» |

### `Screen7Community.jsx`

| Línea | Qué |
|---|---|
| 59 | ranking de usuarios ordenado por `xp_total` |
| 255 | «X XP» junto a cada usuario |

### `Screen5Workspace.jsx`

| Línea | Qué |
|---|---|
| 215 | «X XP» del usuario |

---

## 4. Resumen del choque

- La **Semana 1** del roadmap dice explícitamente «barras de experiencia», y
  `Screen3Dashboard.jsx:213` es literalmente una barra de experiencia.
- El ranking de `Screen7Community.jsx:59` ordena por `xp_total`: si el campo
  desaparece, hay que decidir por qué se ordena.
- `xp_total` es `nullable=False` en la tabla `users` y `UserOut` lo devuelve
  siempre, así que quitarlo del backend implica migración y cambio de contrato.
- Retirarlo solo de la UI dejaría el backend calculando XP, niveles y rachas que
  nadie muestra; retirarlo de ambos lados es un cambio de esquema.

**Nada de lo anterior se ha modificado.** Decisión de Alex y Matías.
