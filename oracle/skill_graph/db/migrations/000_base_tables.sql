-- ============================================================
-- Migration 000: Minimal DELPHOS base tables required by TSG
-- These will be replaced/extended by the full DELPHOS backend
-- Run: psql $DATABASE_URL -f 000_base_tables.sql
-- ============================================================

BEGIN;

-- Users (minimal - full schema lives in DELPHOS backend)
CREATE TABLE IF NOT EXISTS usuarios (
  id                       SERIAL PRIMARY KEY,
  nombre_completo          VARCHAR(200)  NOT NULL,
  email                    VARCHAR(255)  UNIQUE NOT NULL,
  onboarding_completado    BOOLEAN       DEFAULT false,
  paso_onboarding          INTEGER       DEFAULT 1,
  esta_activo              BOOLEAN       DEFAULT true,
  creado_en                TIMESTAMP     DEFAULT now(),
  actualizado_en           TIMESTAMP     DEFAULT now()
);

-- Master skill catalog
CREATE TABLE IF NOT EXISTS habilidades_catalogo (
  id                       SERIAL PRIMARY KEY,
  nombre                   VARCHAR(150)  UNIQUE NOT NULL,
  slug                     VARCHAR(150)  UNIQUE NOT NULL,
  categoria                VARCHAR(50)   NOT NULL, -- tecnica, blanda, herramienta
  descripcion              TEXT,
  habilidad_padre_id       INTEGER       REFERENCES habilidades_catalogo(id),
  nivel_taxonomia          INTEGER       DEFAULT 1,
  demanda_mercado          VARCHAR(20)   DEFAULT 'media',
  tendencia                VARCHAR(20)   DEFAULT 'estable',
  esta_activo              BOOLEAN       DEFAULT true,
  creado_en                TIMESTAMP     DEFAULT now(),
  actualizado_en           TIMESTAMP     DEFAULT now()
);

-- User skill progression
CREATE TABLE IF NOT EXISTS habilidades_usuario (
  id                       SERIAL PRIMARY KEY,
  usuario_id               INTEGER       NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  habilidad_id             INTEGER       NOT NULL REFERENCES habilidades_catalogo(id),
  xp_total                 INTEGER       DEFAULT 0,
  nivel                    INTEGER       DEFAULT 0,
  ultima_practica          TIMESTAMP,
  veces_practicada         INTEGER       DEFAULT 0,
  creado_en                TIMESTAMP     DEFAULT now()
);

-- Simulation modules (minimal)
CREATE TABLE IF NOT EXISTS modulos_simulacion (
  id                       SERIAL PRIMARY KEY,
  titulo                   VARCHAR(200)  NOT NULL,
  esta_activo              BOOLEAN       DEFAULT true,
  creado_en                TIMESTAMP     DEFAULT now()
);

-- Tasks within modules (minimal)
CREATE TABLE IF NOT EXISTS tareas_modulo (
  id                       SERIAL PRIMARY KEY,
  modulo_id                INTEGER       REFERENCES modulos_simulacion(id),
  titulo                   VARCHAR(300)  NOT NULL,
  tipo_tarea               VARCHAR(50)   NOT NULL,
  duracion_estimada_minutos INTEGER      NOT NULL DEFAULT 30,
  esta_activo              BOOLEAN       DEFAULT true,
  creado_en                TIMESTAMP     DEFAULT now()
);

-- Per-user task submissions (minimal)
CREATE TABLE IF NOT EXISTS tareas_usuario (
  id                         SERIAL PRIMARY KEY,
  usuario_id                 INTEGER       NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  tarea_id                   INTEGER       NOT NULL REFERENCES tareas_modulo(id),
  estado                     VARCHAR(50)   DEFAULT 'pendiente',
  respuesta_texto            TEXT,
  total_intentos             INTEGER       DEFAULT 0,
  intento_actual             INTEGER       DEFAULT 1,
  pistas_usadas              JSONB         DEFAULT '[]',
  tiempo_dedicado_minutos    INTEGER       DEFAULT 0,
  auto_evaluacion_calidad    INTEGER,
  auto_evaluacion_dificultad INTEGER,
  feedback_ia_generado       BOOLEAN       DEFAULT false,
  feedback_ia_texto          TEXT,
  feedback_ia_puntos_fuertes JSONB,
  feedback_ia_areas_mejora   JSONB,
  completada_en              TIMESTAMP,
  creado_en                  TIMESTAMP     DEFAULT now(),
  actualizado_en             TIMESTAMP     DEFAULT now()
);

-- Skill weights per task
CREATE TABLE IF NOT EXISTS habilidades_tarea (
  id           SERIAL PRIMARY KEY,
  tarea_id     INTEGER        NOT NULL REFERENCES tareas_modulo(id) ON DELETE CASCADE,
  habilidad_id INTEGER        NOT NULL REFERENCES habilidades_catalogo(id),
  xp_ganado    INTEGER        DEFAULT 10,
  peso         DECIMAL(3,2)   DEFAULT 1.0
);

COMMIT;
