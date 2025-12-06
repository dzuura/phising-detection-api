# PowerShell script untuk menjalankan aplikasi
# Usage: .\run.ps1 [command]

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Available commands:" -ForegroundColor Green
    Write-Host "  .\run.ps1 dev          - Run development server with auto-reload"
    Write-Host "  .\run.ps1 prod         - Run production server"
    Write-Host "  .\run.ps1 install      - Install dependencies"
    Write-Host "  .\run.ps1 test         - Run tests"
    Write-Host "  .\run.ps1 clean        - Clean cache files"
    Write-Host "  .\run.ps1 docker-up    - Start with Docker Compose"
    Write-Host "  .\run.ps1 docker-down  - Stop Docker containers"
    Write-Host "  .\run.ps1 docker-logs  - View Docker logs"
}

function Start-Dev {
    Write-Host "🚀 Starting development server..." -ForegroundColor Cyan
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

function Start-Prod {
    Write-Host "🚀 Starting production server..." -ForegroundColor Cyan
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
}

function Install-Dependencies {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

function Install-DevDependencies {
    Write-Host "📦 Installing all dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
}

function Run-Tests {
    Write-Host "🧪 Running tests..." -ForegroundColor Cyan
    pytest
}

function Run-TestsWithCoverage {
    Write-Host "🧪 Running tests with coverage..." -ForegroundColor Cyan
    pytest --cov=app --cov-report=html
}

function Clean-Cache {
    Write-Host "🧹 Cleaning cache files..." -ForegroundColor Cyan
    Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse
    Get-ChildItem -Path . -Include *.pyc -Recurse -Force | Remove-Item -Force
    Get-ChildItem -Path . -Include *.pyo -Recurse -Force | Remove-Item -Force
    Get-ChildItem -Path . -Include .pytest_cache -Recurse -Force | Remove-Item -Force -Recurse
    Get-ChildItem -Path . -Include htmlcov -Recurse -Force | Remove-Item -Force -Recurse
    Write-Host "✅ Cache cleaned!" -ForegroundColor Green
}

function Start-Docker {
    Write-Host "🐳 Starting Docker Compose..." -ForegroundColor Cyan
    docker-compose up -d
}

function Stop-Docker {
    Write-Host "🐳 Stopping Docker containers..." -ForegroundColor Cyan
    docker-compose down
}

function Show-DockerLogs {
    Write-Host "🐳 Showing Docker logs..." -ForegroundColor Cyan
    docker-compose logs -f
}

function Build-Docker {
    Write-Host "🐳 Building Docker image..." -ForegroundColor Cyan
    docker-compose build
}

# Execute command
switch ($Command.ToLower()) {
    "dev" { Start-Dev }
    "prod" { Start-Prod }
    "install" { Install-Dependencies }
    "install-dev" { Install-DevDependencies }
    "test" { Run-Tests }
    "test-cov" { Run-TestsWithCoverage }
    "clean" { Clean-Cache }
    "docker-up" { Start-Docker }
    "docker-down" { Stop-Docker }
    "docker-logs" { Show-DockerLogs }
    "docker-build" { Build-Docker }
    "help" { Show-Help }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
    }
}
