#!/usr/bin/env bash
set -e

DB_NAME=${1:-hospital_management_db}
DB_USER=${2:-postgres}

psql -U "$DB_USER" -d "$DB_NAME" -f database/schema/01-create-tables.sql
psql -U "$DB_USER" -d "$DB_NAME" -f database/seeds/02-seed-data.sql
psql -U "$DB_USER" -d "$DB_NAME" -f database/queries/03-crud-queries.sql
psql -U "$DB_USER" -d "$DB_NAME" -f database/queries/04-analytical-queries.sql
