#!/usr/bin/env bash
set -euo pipefail

MODE=${1:-all}
DB_NAME=${2:-hospital_management}
DB_USER=${3:-postgres}

run_setup() {
    psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" \
        -f database/schema/01-create-tables.sql
    psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" \
        -f database/seeds/02-seed-data.sql
}

run_validation() {
    psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" \
        -f database/queries/05-validation-counts.sql
}

run_demo() {
    psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" \
        -f database/queries/03-crud-queries.sql
    psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" \
        -f database/queries/04-analytical-queries.sql
}

case "$MODE" in
    setup)
        run_setup
        ;;
    validate)
        run_validation
        ;;
    demo)
        run_demo
        ;;
    all)
        run_setup
        run_validation
        run_demo
        ;;
    *)
        echo "Modo invalido: $MODE" >&2
        echo "Use: setup, validate, demo ou all." >&2
        exit 2
        ;;
esac
