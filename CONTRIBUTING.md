# Contributing Guide

This guide defines how the team should collaborate on this repository.

## Branch Strategy

Use the following flow:

- `main`: final stable version
- `develop`: integration branch
- `feature/<task-name>`: individual work branches

Examples:

```bash
git checkout -b feature/documentation
git checkout -b feature/procedures
git checkout -b feature/orm
```

## Commit Pattern

Use clear commit messages:

```text
docs: update phase 01 report
sql: add analytical query for residents ranking
schema: add database constraints
feat: implement procedure for complete appointment
fix: correct foreign key reference
```

## Pull Request Rules

Before opening a Pull Request:

- Check if SQL scripts run correctly.
- Update documentation if the change affects the project.
- Avoid committing temporary files, database backups or local configuration files.
- Explain what was changed in the Pull Request description.

## Team Responsibilities

Suggested split:

- Database modeling and normalization
- SQL schema and constraints
- Seed data and CRUD queries
- Analytical queries
- Documentation and presentation
- Phase 02 procedures, triggers, views and ORM
