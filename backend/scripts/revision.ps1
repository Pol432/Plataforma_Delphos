param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

if (-not $Message) {
    Write-Host "Usage: .\scripts\revision.ps1 -Message 'your message'"
    exit 1
}

Write-Host "Creating alembic revision: $Message"
docker compose exec api alembic revision --autogenerate -m "$Message"
