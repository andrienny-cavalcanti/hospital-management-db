# Database Execution Guide

Phase 01 uses pure SQL only. No ORM, backend or frontend is required for this execution flow.

## Prerequisites

- PostgreSQL installed and running.
- `psql` available in the terminal.
- A PostgreSQL user with permission to create databases and run scripts.

## Create database

```bash
psql -U postgres
```

```sql
CREATE DATABASE hospital_management_db;
\q
```

## Execute scripts

Run the commands from the repository root:

```bash
psql -U postgres -d hospital_management_db -f database/schema/01-create-tables.sql
psql -U postgres -d hospital_management_db -f database/seeds/02-seed-data.sql
psql -U postgres -d hospital_management_db -f database/queries/05-validation-counts.sql
psql -U postgres -d hospital_management_db -f database/queries/03-crud-queries.sql
psql -U postgres -d hospital_management_db -f database/queries/04-analytical-queries.sql
```

The `database/` directory is the official source for Phase 01 SQL scripts. The `sql/` directory is kept only as a pointer to this structure.

## Recommended order

1. Create tables
2. Insert test data
3. Validate minimum test data
4. Run CRUD queries
5. Run analytical queries

## Script purpose

- `database/schema/01-create-tables.sql`: creates the schema with PK, FK, CHECK, NOT NULL and UNIQUE constraints.
- `database/seeds/02-seed-data.sql`: inserts the minimum test data required for Phase 01.
- `database/queries/05-validation-counts.sql`: checks whether the required minimum records exist.
- `database/queries/03-crud-queries.sql`: demonstrates CRUD and basic queries with SQL only.
- `database/queries/04-analytical-queries.sql`: demonstrates analytical queries with joins, aggregation and filters.
