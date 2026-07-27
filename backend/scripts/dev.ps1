param()

Write-Host "Building and starting containers..."
docker compose up -d --build

Write-Host "Applying Alembic migrations (upgrade head)..."
docker compose exec api alembic upgrade head

Write-Host "Streaming API logs (CTRL+C to stop)..."
docker compose logs -f api
