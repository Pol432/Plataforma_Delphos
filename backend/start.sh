#!/bin/bash
# ============================================
# AURUM DAO API - SCRIPT DE INICIO
# ============================================

set -e

echo "🚀 Iniciando Aurum DAO API..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "✓ PostgreSQL está listo"

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
alembic upgrade head

# Iniciar servidor
echo "✓ Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
