# Script para executar ferramentas de linting e qualidade de código
# Uso: .\lint.ps1 [comando]

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

switch ($Command) {
    "check" {
        Write-Host "🔍 Executando verificações de código..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📝 Flake8..." -ForegroundColor Yellow
        docker-compose run --rm web flake8 apps/
        Write-Host ""
        Write-Host "🔎 Pylint..." -ForegroundColor Yellow
        docker-compose run --rm web pylint apps/
        Write-Host ""
        Write-Host "⚫ Black (check)..." -ForegroundColor Yellow
        docker-compose run --rm web black --check apps/
        Write-Host ""
        Write-Host "📦 Isort (check)..." -ForegroundColor Yellow
        docker-compose run --rm web isort --check apps/
        Write-Host ""
        Write-Host "🔐 Bandit..." -ForegroundColor Yellow
        docker-compose run --rm web bandit -r apps/ -ll
    }
    "format" {
        Write-Host "✨ Formatando código..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⚫ Black..." -ForegroundColor Yellow
        docker-compose run --rm web black apps/
        Write-Host ""
        Write-Host "📦 Isort..." -ForegroundColor Yellow
        docker-compose run --rm web isort apps/
        Write-Host ""
        Write-Host "✅ Código formatado!" -ForegroundColor Green
    }
    "type-check" {
        Write-Host "🔬 Verificando tipos com MyPy..." -ForegroundColor Cyan
        docker-compose run --rm web mypy apps/
    }
    "security" {
        Write-Host "🔐 Análise de segurança com Bandit..." -ForegroundColor Cyan
        docker-compose run --rm web bandit -r apps/ -f json -o bandit-report.json
        docker-compose run --rm web bandit -r apps/
    }
    "all" {
        Write-Host "🚀 Executando todas as verificações..." -ForegroundColor Cyan
        & $PSCommandPath check
        Write-Host ""
        & $PSCommandPath type-check
    }
    default {
        Write-Host "📋 Uso: .\lint.ps1 [comando]" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Comandos disponíveis:"
        Write-Host "  check       - Executa flake8, pylint, black check, isort check e bandit"
        Write-Host "  format      - Formata código com black e isort"
        Write-Host "  type-check  - Verifica tipos com mypy"
        Write-Host "  security    - Análise de segurança com bandit"
        Write-Host "  all         - Executa check + type-check"
        Write-Host ""
        Write-Host "Exemplo: .\lint.ps1 check" -ForegroundColor Yellow
    }
}

