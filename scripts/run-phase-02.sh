#!/usr/bin/env bash
set -euo pipefail

MODE=${1:-all}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ -f backend/.env && -z "${DATABASE_URL:-}" ]]; then
    DATABASE_URL=$(sed -n 's/^DATABASE_URL=//p' backend/.env | head -n 1)
    export DATABASE_URL
fi

DATABASE_URL=${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/hospital_management}
PSQL_DATABASE_URL=${DATABASE_URL/postgresql+psycopg:\/\//postgresql:\/\/}

if [[ -z "${PYTHON:-}" ]]; then
    if [[ -x backend/.venv/bin/python ]]; then
        PYTHON=backend/.venv/bin/python
    else
        PYTHON=backend/.venv/Scripts/python.exe
    fi
fi

run_sql() {
    psql -X "$PSQL_DATABASE_URL" -v ON_ERROR_STOP=1 -f "$1"
}

run_setup() {
    run_sql database/schema/01-create-tables.sql
    run_sql database/seeds/02-seed-data.sql
    run_sql database/migrations/phase-02.sql
}

run_sql_validation() {
    run_sql database/queries/05-validation-counts.sql
    run_sql database/queries/06-validation-triggers.sql
    run_sql database/queries/07-validation-procedures.sql
    run_sql database/queries/08-validation-views.sql
    run_sql database/queries/09-validation-phase-02-summary.sql
}

run_python() {
    PYTHONPATH=backend DATABASE_URL="$DATABASE_URL" "$PYTHON" "$1"
}

run_orm_validation() {
    run_python backend/tests/orm_smoke.py
}

run_concurrency_validation() {
    run_python backend/tests/concurrency_demo.py
}

case "$MODE" in
    setup)
        run_setup
        ;;
    sql)
        run_sql_validation
        ;;
    orm)
        run_orm_validation
        ;;
    concurrency)
        run_concurrency_validation
        ;;
    validate)
        run_sql_validation
        run_orm_validation
        run_concurrency_validation
        ;;
    all)
        run_setup
        run_sql_validation
        run_orm_validation
        run_concurrency_validation
        ;;
    *)
        echo "Modo invalido: $MODE" >&2
        echo "Use: setup, sql, orm, concurrency, validate ou all." >&2
        exit 2
        ;;
esac

echo "Etapa 2 - modo $MODE concluido com sucesso."
