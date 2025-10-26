#!/bin/bash

# Script para executar ferramentas de linting e qualidade de código
# Uso: ./lint.sh [comando]

case "$1" in
    "check")
        echo "🔍 Executando verificações de código..."
        echo ""
        echo "📝 Flake8..."
        docker-compose run --rm web flake8 apps/
        echo ""
        echo "🔎 Pylint..."
        docker-compose run --rm web pylint apps/
        echo ""
        echo "⚫ Black (check)..."
        docker-compose run --rm web black --check apps/
        echo ""
        echo "📦 Isort (check)..."
        docker-compose run --rm web isort --check apps/
        echo ""
        echo "🔐 Bandit..."
        docker-compose run --rm web bandit -r apps/ -ll
        ;;
    "format")
        echo "✨ Formatando código..."
        echo ""
        echo "⚫ Black..."
        docker-compose run --rm web black apps/
        echo ""
        echo "📦 Isort..."
        docker-compose run --rm web isort apps/
        echo ""
        echo "✅ Código formatado!"
        ;;
    "type-check")
        echo "🔬 Verificando tipos com MyPy..."
        docker-compose run --rm web mypy apps/
        ;;
    "security")
        echo "🔐 Análise de segurança com Bandit..."
        docker-compose run --rm web bandit -r apps/ -f json -o bandit-report.json
        docker-compose run --rm web bandit -r apps/
        ;;
    "all")
        echo "🚀 Executando todas as verificações..."
        $0 check
        echo ""
        $0 type-check
        ;;
    *)
        echo "📋 Uso: ./lint.sh [comando]"
        echo ""
        echo "Comandos disponíveis:"
        echo "  check       - Executa flake8, pylint, black check, isort check e bandit"
        echo "  format      - Formata código com black e isort"
        echo "  type-check  - Verifica tipos com mypy"
        echo "  security    - Análise de segurança com bandit"
        echo "  all         - Executa check + type-check"
        echo ""
        echo "Exemplo: ./lint.sh check"
        ;;
esac

