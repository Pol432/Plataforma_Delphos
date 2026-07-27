-- ============================================================
-- TSG Migration 001: Extend habilidades_usuario + new tables
-- Run once: psql $DATABASE_URL -f 001_add_tsg_columns.sql
-- ============================================================

BEGIN;

-- 1. Extend existing habilidades_usuario with TSG fields
ALTER TABLE habilidades_usuario
  ADD COLUMN IF NOT EXISTS confianza           DECIMAL(4,3)  DEFAULT 0,
  ADD COLUMN IF NOT EXISTS velocidad           DECIMAL(6,2)  DEFAULT 0,
  ADD COLUMN IF NOT EXISTS tendencia_ia        VARCHAR(20)   DEFAULT 'unknown',
  ADD COLUMN IF NOT EXISTS aptitud_predicha    DECIMAL(5,2)  DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS fuentes_evidencia   JSONB         DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS ultimo_inferido_en  TIMESTAMP     DEFAULT NULL;

-- Ensure upsert works (required for ON CONFLICT)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'uq_habilidades_usuario_uid_hid'
  ) THEN
    ALTER TABLE habilidades_usuario
      ADD CONSTRAINT uq_habilidades_usuario_uid_hid
      UNIQUE (usuario_id, habilidad_id);
  END IF;
END $$;

-- 2. Onboarding quiz sessions
CREATE TABLE IF NOT EXISTS sesiones_onboarding_habilidades (
  id                    SERIAL PRIMARY KEY,
  usuario_id            INTEGER       NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  respuestas            JSONB         NOT NULL,
  habilidades_inferidas JSONB         DEFAULT '{}',
  confianza_global      DECIMAL(4,3)  DEFAULT 0,
  estado                VARCHAR(20)   DEFAULT 'completado',
  creado_en             TIMESTAMP     DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sesiones_onboarding_usuario
  ON sesiones_onboarding_habilidades(usuario_id);

-- 3. Raw inference log (debug + future retraining)
CREATE TABLE IF NOT EXISTS inferencias_habilidades (
  id               SERIAL PRIMARY KEY,
  usuario_id       INTEGER      NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  tipo_fuente      VARCHAR(50)  NOT NULL,  -- quiz, tarea, transcript, social, behavioral
  referencia_id    INTEGER,
  habilidades_raw  JSONB        NOT NULL,
  confianza        DECIMAL(4,3),
  modelo_version   VARCHAR(50),
  tiempo_ms        INTEGER,
  creado_en        TIMESTAMP    DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_inferencias_usuario
  ON inferencias_habilidades(usuario_id);
CREATE INDEX IF NOT EXISTS idx_inferencias_fuente
  ON inferencias_habilidades(tipo_fuente);

-- 4. Aptitude predictions for skills not yet practiced
CREATE TABLE IF NOT EXISTS aptitudes_predichas (
  id               SERIAL PRIMARY KEY,
  usuario_id       INTEGER      NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  habilidad_id     INTEGER      NOT NULL REFERENCES habilidades_catalogo(id),
  aptitud          DECIMAL(5,2) NOT NULL,
  habilidades_base JSONB,   -- e.g. {"analytical_thinking": 72, "creativity": 65}
  confianza        DECIMAL(4,3),
  creado_en        TIMESTAMP    DEFAULT now(),
  CONSTRAINT uq_aptitud_usuario_habilidad UNIQUE (usuario_id, habilidad_id)
);

CREATE INDEX IF NOT EXISTS idx_aptitudes_usuario
  ON aptitudes_predichas(usuario_id);

COMMIT;
