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
- 3NF normalization documentation
- Phase 01 report
- ER diagram export

## SQL Execution Order

Execute the scripts in this order:

```bash
psql -U postgres -d hospital_management_db -f database/schema/01-create-tables.sql
psql -U postgres -d hospital_management_db -f database/seeds/02-seed-data.sql
psql -U postgres -d hospital_management_db -f database/queries/03-crud-queries.sql
psql -U postgres -d hospital_management_db -f database/queries/04-analytical-queries.sql
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
