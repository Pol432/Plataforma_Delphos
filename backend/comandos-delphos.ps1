# ============================================================================
# Comandos Docker para Delphos API
# ============================================================================
# Uso: . .\comandos-delphos.ps1  (cargar en sesión actual)
# ============================================================================

# Detecta automáticamente la carpeta actual, ya no importa cómo se llame
$Global:DELPHOS_PROJECT = $PSScriptRoot

function delphos-start {
    <#
    .SYNOPSIS
    Inicia todos los servicios de Delphos
    #>
    Write-Host "🚀 Iniciando Delphos API..." -ForegroundColor Cyan
    Set-Location $Global:DELPHOS_PROJECT
    docker compose up -d
    Start-Sleep -Seconds 5
    docker compose ps
    Write-Host "`n✓ Servicios iniciados" -ForegroundColor Green
    Write-Host "📝 API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
}

function delphos-stop {
    <#
    .SYNOPSIS
    Detiene todos los servicios de Delphos
    #>
    Write-Host "⏸️  Deteniendo Delphos API..." -ForegroundColor Yellow
    Set-Location $Global:DELPHOS_PROJECT
    docker compose down
    Write-Host "✓ Servicios detenidos" -ForegroundColor Green
}

function delphos-restart {
    <#
    .SYNOPSIS
    Reinicia todos los servicios de Delphos
    #>
    Write-Host "🔄 Reiniciando Delphos API..." -ForegroundColor Cyan
    delphos-stop
    Start-Sleep -Seconds 2
    delphos-start
}

function delphos-logs {
    <#
    .SYNOPSIS
    Muestra logs de los servicios
    .PARAMETER Service
    Servicio específico (web o db). Si no se especifica, muestra todos.
    .PARAMETER Follow
    Seguir logs en tiempo real
    #>
    param(
        [string]$Service = "",
        [switch]$Follow
    )
    
    Set-Location $Global:DELPHOS_PROJECT
    
    if ($Follow) {
        if ($Service) {
            docker compose logs -f $Service
        } else {
            docker compose logs -f
        }
    } else {
        if ($Service) {
            docker compose logs --tail=100 $Service
        } else {
            docker compose logs --tail=100
        }
    }
}

function delphos-shell {
    <#
    .SYNOPSIS
    Abre un shell interactivo en el contenedor especificado
    .PARAMETER Service
    Servicio (web o db). Por defecto: web
    #>
    param(
        [string]$Service = "web"
    )
    
    Write-Host "🐚 Abriendo shell en contenedor: $Service" -ForegroundColor Cyan
    Set-Location $Global:DELPHOS_PROJECT
    
    if ($Service -eq "db") {
        # Nota: Aquí se conecta a la base de datos que está en el docker compose.yml
        docker compose exec db psql -U postgres -d aurum_dao
    } else {
        docker compose exec web /bin/bash
    }
}

function delphos-migrate {
    <#
    .SYNOPSIS
    Ejecuta migraciones de Alembic
    .PARAMETER Action
    Acción: upgrade, downgrade, revision, history
    .PARAMETER Target
    Target para upgrade/downgrade (por defecto: head)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("upgrade", "downgrade", "revision", "history", "current")]
        [string]$Action,
        [string]$Target = "head",
        [string]$Message = ""
    )
    
    Set-Location $Global:DELPHOS_PROJECT
    
    switch ($Action) {
        "upgrade" {
            Write-Host "⬆️  Aplicando migraciones..." -ForegroundColor Cyan
            docker compose exec web alembic upgrade $Target
        }
        "downgrade" {
            Write-Host "⬇️  Revirtiendo migraciones..." -ForegroundColor Yellow
            docker compose exec web alembic downgrade $Target
        }
        "revision" {
            if (-not $Message) {
                Write-Host "❌ Se requiere un mensaje para la revisión" -ForegroundColor Red
                return
            }
            Write-Host "📝 Creando nueva revisión..." -ForegroundColor Cyan
            docker compose exec web alembic revision --autogenerate -m "$Message"
        }
        "history" {
            docker compose exec web alembic history
        }
        "current" {
            docker compose exec web alembic current
        }
    }
}

function delphos-test {
    <#
    .SYNOPSIS
    Ejecuta tests con pytest
    .PARAMETER Path
    Ruta específica de tests. Por defecto: todos
    #>
    param(
        [string]$Path = "tests/"
    )
    
    Write-Host "🧪 Ejecutando tests..." -ForegroundColor Cyan
    Set-Location $Global:DELPHOS_PROJECT
    docker compose exec web pytest $Path -v
}

function delphos-rebuild {
    <#
    .SYNOPSIS
    Reconstruye las imágenes de Docker desde cero
    #>
    Write-Host "🔨 Reconstruyendo imágenes..." -ForegroundColor Cyan
    Set-Location $Global:DELPHOS_PROJECT
    docker compose down
    docker compose build --no-cache
    docker compose up -d
    Write-Host "✓ Reconstrucción completada" -ForegroundColor Green
}

function delphos-status {
    <#
    .SYNOPSIS
    Muestra el estado de todos los servicios
    #>
    Write-Host "`n📊 Estado de Delphos API" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Set-Location $Global:DELPHOS_PROJECT
    docker compose ps
    Write-Host "`n📝 API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
    Write-Host "🗄️  PostgreSQL: localhost:5432" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
}

function delphos-db-reset {
    <#
    .SYNOPSIS
    Reinicia completamente la base de datos (¡PELIGRO!)
    #>
    Write-Host "⚠️  ADVERTENCIA: Esto eliminará TODOS los datos" -ForegroundColor Red
    $confirm = Read-Host "¿Estás seguro? (escribe 'SI' para confirmar)"
    
    if ($confirm -eq "SI") {
        Write-Host "🗑️  Eliminando base de datos..." -ForegroundColor Yellow
        Set-Location $Global:DELPHOS_PROJECT
        docker compose down -v
        docker compose up -d db
        Start-Sleep -Seconds 5
        docker compose up -d web
        Start-Sleep -Seconds 3
        Write-Host "🔄 Aplicando migraciones..." -ForegroundColor Cyan
        docker compose exec web alembic upgrade head
        Write-Host "✓ Base de datos reiniciada" -ForegroundColor Green
    } else {
        Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    }
}

function delphos-help {
    <#
    .SYNOPSIS
    Muestra ayuda de comandos disponibles
    #>
    Write-Host "`n🎯 Comandos disponibles para Delphos API" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "  delphos-start         " -NoNewline; Write-Host "Inicia todos los servicios" -ForegroundColor Gray
    Write-Host "  delphos-stop          " -NoNewline; Write-Host "Detiene todos los servicios" -ForegroundColor Gray
    Write-Host "  delphos-restart       " -NoNewline; Write-Host "Reinicia todos los servicios" -ForegroundColor Gray
    Write-Host "  delphos-logs [srv]    " -NoNewline; Write-Host "Muestra logs (usa -Follow para seguir)" -ForegroundColor Gray
    Write-Host "  delphos-shell [srv]   " -NoNewline; Write-Host "Abre shell en contenedor (web o db)" -ForegroundColor Gray
    Write-Host "  delphos-migrate       " -NoNewline; Write-Host "Ejecuta migraciones de Alembic" -ForegroundColor Gray
    Write-Host "  delphos-test [path]   " -NoNewline; Write-Host "Ejecuta tests con pytest" -ForegroundColor Gray
    Write-Host "  delphos-rebuild       " -NoNewline; Write-Host "Reconstruye imágenes desde cero" -ForegroundColor Gray
    Write-Host "  delphos-status        " -NoNewline; Write-Host "Muestra estado de servicios" -ForegroundColor Gray
    Write-Host "  delphos-db-reset      " -NoNewline; Write-Host "Reinicia la base de datos (¡PELIGRO!)" -ForegroundColor Gray
    Write-Host "  delphos-help          " -NoNewline; Write-Host "Muestra esta ayuda" -ForegroundColor Gray
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
}

# Mensaje de bienvenida
Write-Host "✓ Comandos Delphos cargados exitosamente" -ForegroundColor Green
Write-Host "  Usa 'delphos-help' para ver todos los comandos disponibles" -ForegroundColor Gray
