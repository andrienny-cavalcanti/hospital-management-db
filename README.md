# Hospital Management System DB

Academic database project for a Hospital Management System developed for the Database course.

The project is organized to support two academic phases:

- **Phase 01 — Foundation:** relational modeling, SQL schema, seed data, CRUD queries and analytical queries.
- **Phase 02 — Advanced:** stored procedures, triggers, views, ORM implementation and transaction control.

## Project Identity

- **Institutional context:** Hospital Universitário Dra. Yuska Maritan Brito
- **Repository name:** `hospital-management-db`
- **Local folder name:** `Hospital-Management-System-DB`
- **Main database:** PostgreSQL
- **Current status:** Phase 01 completed and Phase 02 prepared

## Repository Structure

```text
Hospital-Management-System-DB
├── .github
│   ├── ISSUE_TEMPLATE
│   └── workflows
├── docs
│   ├── 01-project
│   ├── 02-analysis
│   ├── 03-modeling
│   ├── 04-database
│   ├── 05-api
│   ├── 06-orm
│   ├── 07-tests
│   └── assets
├── database
│   ├── schema
│   ├── migrations
│   ├── seeds
│   ├── procedures
│   ├── triggers
│   ├── views
│   ├── queries
│   └── backups
├── backend
├── frontend
├── diagrams
│   ├── conceptual
│   ├── logical
│   ├── physical
│   └── exports
├── reports
│   ├── phase-01
│   └── phase-02
├── presentations
├── tests
├── scripts
├── CONTRIBUTING.md
├── PROJECT_STATUS.md
├── ROADMAP.md
├── CHANGELOG.md
└── README.md
```

## Phase 01 Deliverables

- Complete relational database schema
- Test data inserts
- CRUD operations using pure SQL
- Basic and analytical queries
- Relational model documentation
- ER diagram justification with cardinalities and specialization decisions
- 3NF normalization documentation
- Phase 01 report
- ER diagram export

## Installation and Execution

Phase 01 uses **pure SQL only**. No ORM, backend or frontend is required to execute this delivery.

### Prerequisites

- PostgreSQL installed and running.
- `psql` available in the terminal.
- A PostgreSQL user with permission to create databases and execute scripts.

### 1. Create the database

Access PostgreSQL and create the project database:

```bash
psql -U postgres
```

```sql
CREATE DATABASE hospital_management_db;
\q
```

If the database already exists and you want to recreate the schema, the creation script can be executed again because it starts by dropping the project tables with `CASCADE`.

### 2. Run the Phase 01 scripts

From the repository root, execute the scripts in this order:

```bash
psql -U postgres -d hospital_management_db -f database/schema/01-create-tables.sql
psql -U postgres -d hospital_management_db -f database/seeds/02-seed-data.sql
psql -U postgres -d hospital_management_db -f database/queries/05-validation-counts.sql
psql -U postgres -d hospital_management_db -f database/queries/03-crud-queries.sql
psql -U postgres -d hospital_management_db -f database/queries/04-analytical-queries.sql
```

The `database/` directory is the official source for Phase 01 SQL scripts. The `sql/` directory is kept only as a pointer to avoid duplicated scripts and version drift.

### 3. What each script does

- `database/schema/01-create-tables.sql`: creates all Phase 01 tables, primary keys, foreign keys, checks, unique constraints and indexes.
- `database/seeds/02-seed-data.sql`: inserts test data required by the statement.
- `database/queries/05-validation-counts.sql`: validates the minimum test data required for Phase 01.
- `database/queries/03-crud-queries.sql`: demonstrates CRUD and basic queries using SQL only.
- `database/queries/04-analytical-queries.sql`: runs the analytical queries required for Phase 01.

### 4. Documentation for review

- Conceptual DER: `diagrams/conceptual/er-diagram.mmd`
- DER export guide: `diagrams/conceptual/README.md`
- DER justification: `docs/03-modeling/er-justification.md`
- Relational model: `docs/03-modeling/relational-model.md`
- Normalization evidence: `docs/03-modeling/normalization-3nf.md`
- Execution guide: `docs/04-database/execution-guide.md`

## Optional Swagger API

The project also includes an optional FastAPI backend in `backend/` to make data manipulation easier through Swagger UI.

This API is only a support interface. The official Phase 01 delivery remains the pure SQL scripts in `database/`.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --env-file .env
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Recommended Git Flow

Main branches:

- `main`: stable version for delivery
- `develop`: integration branch for team work

Feature branches:

- `feature/database`
- `feature/documentation`
- `feature/procedures`
- `feature/triggers`
- `feature/views`
- `feature/orm`
- `feature/transactions`

## Team Workflow

1. Always update your local branch before working.
2. Create a new feature branch.
3. Commit with clear messages.
4. Push your branch.
5. Open a Pull Request into `develop`.
6. Merge into `main` only after review.

## Academic Objective

This repository demonstrates database design and implementation through conceptual, logical and physical modeling, normalization, SQL operations, analytical queries and preparation for advanced database resources.
