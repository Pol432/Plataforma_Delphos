.PHONY: help build up down restart logs shell db-shell test migrate migrate-auto clean

help: ## Mostrar ayuda
    @echo "Comandos disponibles:"
    @echo "  make build        - Construir imágenes Docker"
    @echo "  make up           - Iniciar servicios"
    @echo "  make down         - Detener servicios"
    @echo "  make restart      - Reiniciar servicios"
    @echo "  make logs         - Ver logs"
    @echo "  make shell        - Acceder a shell del contenedor"
    @echo "  make db-shell     - Acceder a PostgreSQL"
    @echo "  make test         - Ejecutar tests"
    @echo "  make migrate      - Aplicar migraciones"
    @echo "  make migrate-auto - Crear migración automática"
    @echo "  make clean        - Limpiar todo (¡CUIDADO!)"

build: ## Construir imágenes
    docker-compose build

up: ## Iniciar servicios
    docker-compose up -d

down: ## Detener servicios
    docker-compose down

restart: ## Reiniciar servicios
    docker-compose restart

logs: ## Ver logs
    docker-compose logs -f web

logs-db: ## Ver logs de DB
    docker-compose logs -f db

shell: ## Acceder al contenedor
    docker-compose exec web bash

db-shell: ## Acceder a PostgreSQL
    docker-compose exec db psql -U postgres -d aurum_dao

test: ## Ejecutar tests
    docker-compose exec web pytest tests/ -v -s

test-cov: ## Ejecutar tests con cobertura
    docker-compose exec web pytest tests/ -v --cov=app --cov-report=html

migrate: ## Aplicar migraciones
    docker-compose exec web alembic upgrade head

migrate-auto: ## Crear migración automática
    docker-compose exec web alembic revision --autogenerate -m "$(msg)"

migrate-rollback: ## Revertir última migración
    docker-compose exec web alembic downgrade -1

ps: ## Ver contenedores
    docker-compose ps

clean: ## Limpiar todo (¡CUIDADO!)
    docker-compose down -v
    docker system prune -af

seed: ## Poblar base de datos con datos de prueba
    docker-compose exec web python -m app.scripts.seed_data
